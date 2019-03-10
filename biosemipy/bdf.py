"""
Python module to read BioSemi EEG data files.
"""
import numpy as np
from numba import jit


class BDF:
    """BioSemi Data Class"""

    def __init__(self, fname=None, hdr_only=False, chans=None):
        """
        Read BioSemi EEG datafile header plus data (default)
        See https://www.biosemi.com/faq_file_format.htm for details

        :param fname: str
        :param hdr_only: bool (default: True)
        :param chans: list (default: all channels)
        """

        self.fname = fname
        self.hdr = dict()
        self.data = None
        self.time = None
        self.trig = None
        self.status = None

        if fname is not None:
            self.read(fname, hdr_only=hdr_only, chans=chans)

    def __str__(self):
        """
        Just print out some useful information.
        """
        name = "Filename: " + str(self.fname)
        n_chans = "Number of Channels: " + str(self.hdr["n_chans"])
        labels = "Channel Labels: " + str(self.hdr["labels"])
        freq = "Sampling Frequency: " + str(self.hdr["freq"][0])

        return "{}\n{}\n{}\n{}".format(name, n_chans, labels, freq)

    def __repr__(self):
        return self.__str__()

    def read(self, fname, hdr_only=False, chans=None):

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
            self.hdr["pmin"] = np.array([int(f.read(8)) for _ in ch])
            self.hdr["pmax"] = np.array([int(f.read(8)) for _ in ch])
            self.hdr["dmin"] = np.array([int(f.read(8)) for _ in ch])
            self.hdr["dmax"] = np.array([int(f.read(8)) for _ in ch])
            self.hdr["filter"] = [f.read(80).decode().strip() for _ in ch]
            self.hdr["n_samps"] = [np.int(f.read(8)) for _ in ch]
            self.hdr["reserved"] = [f.read(32).decode().strip() for _ in ch]
            self.hdr["scale"] = np.array(
                (self.hdr["pmax"] - self.hdr["pmin"]) /
                (self.hdr["dmax"] - self.hdr["dmin"]))
            self.hdr["freq"] = [int(self.hdr["n_samps"][i] /
                                    self.hdr["dur_recs"]) for i in ch]

            if hdr_only:
                return

            if chans:  # specific selection made
                chans = self._channel_idx(chans)
            else:  # read all channels
                chans = list(range(self.hdr["n_chans"]))

            bdf_dat = np.fromfile(f, dtype=np.dtype("uint8"))

            self._bdf2matrix(bdf_dat, chans)
            self._trigger_info()
            self.time = np.arange(0, np.size(self.data, 1)) / self.hdr["freq"][0]
            self._update_header(chans)

    def write(self, fname=None):

        if not fname:
            fname = self.fname
        print("Writing to file {}".format(fname))

        hdr = [0xFF]
        [hdr.append(ord(i)) for i in self.hdr["id2"]]
        [hdr.append(ord(i)) for i in self.hdr["text1"]]
        [hdr.append(ord(i)) for i in self.hdr["text2"]]
        [hdr.append(ord(i)) for i in self.hdr["date"]]
        [hdr.append(ord(i)) for i in self.hdr["time"]]
        [hdr.append(ord(i)) for i in "{0:<8}".format(self.hdr["n_bytes_hdr"])]
        [hdr.append(ord(i)) for i in "{0:<44}".format(self.hdr["format"])]
        [hdr.append(ord(i)) for i in "{0:<8}".format(self.hdr["n_recs"])]
        [hdr.append(ord(i)) for i in "{0:<8}".format(self.hdr["dur_recs"])]
        [hdr.append(ord(i)) for i in "{0:<4}".format(self.hdr["n_chans"])]
        [hdr.append(ord(j)) for i in self.hdr["labels"] for j in "{0:<16}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["type"] for j in "{0:<80}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["unit"] for j in "{0:<8}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["pmin"] for j in "{0:<8}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["pmax"] for j in "{0:<8}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["dmin"] for j in "{0:<8}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["dmax"] for j in "{0:<8}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["filter"] for j in "{0:<80}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["n_samps"] for j in "{0:<8}".format(i)]
        [hdr.append(ord(j)) for i in self.hdr["reserved"] for j in "{0:<32}".format(i)]

        sf = np.array(self.hdr["scale"][:-1])
        data = np.int32(np.round(self.data / sf[:, None]))
        bdf = _matrix2bdf(data,
                          self.trig["raw"],
                          self.status,
                          self.hdr["n_recs"],
                          self.hdr["n_samps"][0],
                          self.hdr["n_chans"])

        dat = np.concatenate([hdr, bdf])
        dat.astype("uint8").tofile(fname)

    def merge(self, fname, *args):
        """Merge bdf files."""

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
            self.trig["raw"] = np.concatenate([self.trig["raw"],
                                               x.trig["raw"]])
            self.status = np.concatenate([self.status, x.status])

        self._trigger_info()
        self.time = np.arange(0, np.size(self.data, 1)) / self.hdr["freq"][0]

    def delete_channels(self, chans):
        """Delete specific data channels."""
        chans = self._channel_idx(chans)
        chans = list(set(range(self.hdr["n_chans"])).difference(chans[:-1]))
        self.data = self.data[chans[:-1], :]
        self._update_header(chans)

    def select_channels(self, chans):
        """Select specific data channels."""
        chans = self._channel_idx(chans)
        self.data = self.data[chans[:-1], :]
        self._update_header(chans)

    def _channel_idx(self, chans):
        """
        Check requested chan_in is in the datafile and if label
        entered is a string, convert it to an index number.
        :param chans: list
        :return: list
        """
        chan_out = []
        if -1 in chans:
            chans[chans.index(-1)] = len(self.hdr["labels"])

        for chan in chans:
            if isinstance(chan, str) and chan in self.hdr["labels"][:-1]:
                chan_out.append(self.hdr["labels"].index(chan))
            elif isinstance(chan, str) and chan == self.hdr["labels"][-1]:
                print("Channel:'{}' is trigger channel!".format(chan))
            elif isinstance(chan, int) and 0 < chan < (self.hdr["n_chans"]):
                chan_out.append(chan - 1)  # zero index
            elif isinstance(chan, int) and chan == (self.hdr["n_chans"]):
                print("Channel:'{}' is trigger channel!".format(chan))
            else:
                raise Exception("Channel:'{}' not in bdf file!".format(chan))

        chan_out.append(self.hdr["n_chans"] - 1)

        return np.sort(np.unique(chan_out)).tolist()

    def _bdf2matrix(self, bdf_dat, chans):

        data, trig, status = _bdf2matrix(bdf_dat,
                                         chans,
                                         self.hdr["scale"],
                                         self.hdr["n_chans"],
                                         self.hdr["n_recs"],
                                         self.hdr["n_samps"][0])

        self.data = data
        self.trig = {"raw": trig}
        self.status = status

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


@jit(nopython=True)
def _bdf2matrix(bdf_dat, chans, scale, n_chans, n_recs, n_samps):
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
                if chan < (n_chans - 1):
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


@jit(nopython=True)
def _matrix2bdf(data, trig, status, n_recs, n_samps, n_chans):
    """
    Take n channels and n time points and convert
    to 1 * (3*n_recs*n_chans*_n_samps) numpy array of type
    uint8 to be written to file.
    """

    bdf = np.zeros(3*(n_recs*n_chans*n_samps), dtype=np.uint8)

    pos = 0
    for rec in range(n_recs):
        for chan in range(n_chans):
            if chan < (n_chans - 1):
                for samp in range(n_samps):
                    val = data[chan, rec*n_samps + samp]
                    bdf[pos] = np.uint8(val)
                    bdf[pos + 1] = np.uint8(val >> 8)
                    bdf[pos + 2] = np.uint8(val >> 16)
                    pos += 3
            else:
                for samp in range(n_samps):
                    trig_val = trig[rec*n_samps+samp]
                    status_val = status[rec*n_samps+samp]
                    bdf[pos] = np.uint8(trig_val)
                    bdf[pos+1] = np.uint8(status_val) >> 8
                    bdf[pos+2] = np.uint8(status_val)
                    pos += 3

    return bdf

