"""
Python module to read BioSemi EEG data files.
"""
import numpy as np
from numba import jit


class BDF(object):
    """BioSemi Data Class"""

    def __init__(self, fname, hdr_only=False, chans=None, use_numba=True):
        """
        Read BioSemi EEG datafile header plus data (default)
        See https://www.biosemi.com/faq_file_format.htm for details

        :param fname: str
        :param hdr_only: bool (default: True)
        :param chans: list (default: all channels)
        :param use_numba: bool (default: True)
        """

        self.fname = fname
        self.hdr = dict()
        self.data = None
        self.time = None
        self.trig = None
        self.status = None

        with open(fname, "rb") as f:
            self.hdr["id1"] = f.read(1)
            self.hdr["id2"] = f.read(7).decode()
            self.hdr["text1"] = f.read(80).decode()
            self.hdr["text2"] = f.read(80).decode()
            self.hdr["date"] = f.read(8).decode()
            self.hdr["time"] = f.read(8).decode()
            self.hdr["n_bytes_hdr"] = int(f.read(8))
            self.hdr["format"] = f.read(44).decode().strip()
            self.hdr["n_recs"] = int(f.read(8))
            self.hdr["dur_recs"] = int(f.read(8))
            self.hdr["n_chans"] = int(f.read(4))
            ch = range(self.hdr["n_chans"])
            self.hdr["labels"] = [f.read(16).decode().strip() for _ in ch]
            self.hdr["type"] = [f.read(80).decode().strip() for _ in ch]
            self.hdr["unit"] = [f.read(8).decode().strip() for _ in ch]
            self.hdr["pmin"] = np.asarray([int(f.read(8)) for _ in ch])
            self.hdr["pmax"] = np.asarray([int(f.read(8)) for _ in ch])
            self.hdr["dmin"] = np.asarray([int(f.read(8)) for _ in ch])
            self.hdr["dmax"] = np.asarray([int(f.read(8)) for _ in ch])
            self.hdr["filter"] = [f.read(80).decode().strip() for _ in ch]
            self.hdr["n_samps"] = [np.int(f.read(8)) for _ in ch]
            self.hdr["reserved"] = [f.read(32).decode().strip() for _ in ch]
            self.hdr["scale"] = np.float32(
                (self.hdr["pmax"] - self.hdr["pmin"]) /
                (self.hdr["dmax"] - self.hdr["dmin"]))
            self.hdr["freq"] = [int(self.hdr["n_samps"][i] /
                                    self.hdr["dur_recs"]) for i in ch]

            if not hdr_only:
                self._get_data(f, chans, use_numba=use_numba)

    def __str__(self):
        """
        Just print out some useful information
        """
        name = "Filename: " + str(self.fname)
        n_chans = "Number of Channels: " + str(self.hdr["n_chans"])
        labels = "Channel Labels: " + str(self.hdr["labels"])
        freq = "Sampling Frequency: " + str(self.hdr["freq"][0])

        return "{}\n{}\n{}\n{}".format(name, n_chans, labels, freq)

    def __repr__(self):
        return self.__str__()

    def _get_data(self, f, chans, use_numba=True):

        if not chans:  # read all channels
            chans = list(range(self.hdr["n_chans"]))
        else:  # specific selection made
            chans = self.channel_idx(chans)

        bdf_dat = np.fromfile(f, dtype=np.dtype("uint8"))
        if use_numba:
            self._bdf2matrix_numba(bdf_dat, chans)
        else:
            self._bdf2matrix_numpy(bdf_dat, chans)

        self._trigger_info()
        self.time = np.arange(0, np.size(self.data, 1)) / self.hdr["freq"][0]
        self._update_header(chans)

    def _bdf2matrix_numba(self, bdf_dat, chans):

        n_chans = self.hdr["n_chans"]
        n_recs = self.hdr["n_recs"]
        n_samps = self.hdr["n_samps"][0]
        scale = self.hdr["scale"]

        data, trig, status = _bdf2matrix_numba(bdf_dat, scale, chans,
                                               n_chans, n_recs, n_samps)

        self.data = data
        self.trig = {"raw": trig}
        self.status = status

    def _bdf2matrix_numpy(self, bdf_dat, chans):
        """
        Take remaining data in bdf_dat and assign to n channels by
        n time points numpy matrix. (NB. numba equivalent function
        should be faster.)
        """

        n_chans = self.hdr["n_chans"]
        n_recs = self.hdr["n_recs"]
        n_samps = self.hdr["n_samps"][0]
        scale = self.hdr["scale"]

        self.data = np.zeros((len(chans) - 1, n_recs * n_samps),
                             dtype=np.float32)

        p1 = n_samps * 3
        p2 = p1 * n_chans * n_recs
        ch_count = 0
        for ch in chans[:-1]:
            start = np.arange(ch * p1, p2, n_chans * p1)
            idx = np.add.outer(start, np.arange(p1))

            # channel data
            cd = bdf_dat[idx].reshape(-1, 3).astype(np.int32)
            cd = (cd[:, 0] << 8 | (cd[:, 1] << 16) | (-(-cd[:, 2] << 24))) >> 8
            self.data[ch_count, :] = cd.astype(np.float32) * scale[ch]
            ch_count += 1

        # trigger data
        start = np.arange((n_chans - 1) * p1, p2, n_chans * p1)
        idx = np.add.outer(start, np.arange(p1))
        cd = bdf_dat[idx].reshape(-1, 3).astype(np.int16)

        self.trig = {"raw": (cd[:, 0] | cd[:, 1] << 8)}
        self.status = cd[:, 2]

    def _update_header(self, chans):
        """
        Update the information stored in the header field if a subset of
        channels are selected.
        """
        self.hdr["n_chans"] = len(chans)
        fields = ["labels", "type", "unit", "pmin", "pmax", "dmin", "dmax",
                  "filter", "n_samps", "reserved", "scale", "freq"]
        for field in fields:
            self.hdr[field] = [self.hdr[field][x] for x in chans]
        self.hdr["n_bytes_hdr"] = (self.hdr["n_chans"] + 1) * 256

    def _trigger_info(self):
        """
        Provide detailed trigger information. Creates trig dict with the
        following fields:
        raw: data from the trigger channel
        idx: index within vector of trigger onset
        val: trigger value
        count: trigger value and corresponding count
        time: trigger value and corresponding time
        """
        self.trig["idx"] = np.where(np.diff(self.trig["raw"]) >= 1)[0] + 1
        self.trig["val"] = self.trig["raw"][self.trig["idx"]]

        values, count = np.unique(self.trig["val"], return_counts=True)
        self.trig["count"] = dict(zip(values, count))

        time = np.append(0, np.diff(self.trig["idx"])) / self.hdr["freq"][0]
        self.trig["time"] = np.vstack([self.trig["val"], time])

    def merge(self, fname, *args):

        data_to_merge = list(args)

        for x in data_to_merge:
            if self.hdr["n_chans"] != x.hdr["n_chans"]:
                print("Different numbers of channels!")
                return
            if self.hdr["labels"] != x.hdr["labels"]:
                print("Different channel labels!")
                return
            if self.hdr["freq"][0] != x.hdr["freq"][0]:
                print("Different sample rate!")
                return

        self.fname = fname
        for x in data_to_merge:
            self.hdr["n_recs"] += x.hdr["n_recs"]
            self.data = np.concatenate([self.data, x.data], axis=1)
            self.trig["raw"] = np.concatenate([self.trig["raw"], x.trig["raw"]])
            self.status = np.concatenate([self.status, x.status])

        self._trigger_info()
        self.time = np.arange(0, np.size(self.data, 1)) / self.hdr["freq"][0]

    def channel_idx(self, chan_in):
        """
        Check requested chan_in is in the datafile and if label
        entered is a string, convert it to an index number.
        :param chan_in: list
        :return: list
        """
        chan_out = []
        if -1 in chan_in:
            chan_in[chan_in.index(-1)] = len(self.hdr["labels"])

        for x in chan_in:
            if isinstance(x, str) and x in self.hdr["labels"]:
                chan_out.append(self.hdr["labels"].index(x))
            elif isinstance(x, int) and 0 < x <= self.hdr["n_chans"]:
                chan_out.append(x - 1)  # zero index
            else:
                print("Channel:'{}' is not in bdf file!".format(x))
        chan_out.append(self.hdr["n_chans"] - 1)

        return np.sort(np.unique(chan_out)).tolist()


@jit(nopython=True)
def _bdf2matrix_numba(bdf_dat, scale, chans, n_chans, n_recs, n_samps):
    """
    Take remaining data in bdf_dat and assign to n channels by
    n time points numpy matrix.
    """

    data = np.zeros((len(chans) - 1, n_recs * n_samps), dtype=np.float32)
    trig = np.zeros(n_recs * n_samps, dtype=np.int16)
    status = np.zeros(n_recs * n_samps, dtype=np.int16)

    pos = 0
    for rec in range(n_recs):
        idx = 0
        for chan in range(n_chans):
            if chan in chans:
                if chan < (n_chans-1):
                    for samp in range(n_samps):
                        val1 = np.int32(bdf_dat[pos]) << 8
                        val2 = np.int32(bdf_dat[pos+1]) << 16
                        val3 = -(np.int32(-bdf_dat[pos+2])) << 24
                        val = ((val1 | val2 | val3) >> 8) * scale[chan]
                        data[idx, rec*n_samps+samp] = np.float32(val)
                        pos += 3
                else:  # last channel is always Status channel
                    for samp in range(n_samps):
                        val1 = np.int16(bdf_dat[pos])
                        val2 = np.int16(bdf_dat[pos+1])
                        val = val1 | (val2 << 8)
                        trig[rec*n_samps+samp] = val
                        status[rec*n_samps+samp] = np.int16(bdf_dat[pos+2])
                        pos += 3
                idx += 1
            else:
                pos += n_samps*3

    return data, trig, status
