"""Basic unittests for biosemipy"""

import unittest
import numpy as np
from biosemipy.bdf import BDF


class BDFTestCase(unittest.TestCase):
    """Tests for BDF"""

    def test_bdf1(self):
        """Newtest17-256 read"""

        dat = BDF("Newtest17-256.bdf")

        self.assertEqual(dat.hdr["n_bytes_hdr"], 18*256)
        self.assertEqual(dat.hdr["n_chans"], 17)
        self.assertEqual(dat.hdr["n_recs"], 60)
        self.assertEqual(dat.hdr["freq"][0], 256)
        self.assertEqual(np.shape(dat.data), (16, 15360))
        self.assertEqual(dat.trig["idx"][0], 414)
        self.assertEqual(dat.trig["val"][0], 255)
        self.assertEqual(dat.trig["count"][255], 40)

    def test_bdf2(self):
        """Newtest17-256 read header only"""

        dat = BDF("Newtest17-256.bdf", hdr_only=True)

        self.assertEqual(dat.hdr["n_bytes_hdr"], 18*256)
        self.assertEqual(dat.hdr["n_chans"], 17)
        self.assertEqual(dat.hdr["n_recs"], 60)
        self.assertEqual(dat.hdr["freq"][0], 256)
        self.assertIsNone(dat.data)
        self.assertIsNone(dat.trig)
        self.assertIsNone(dat.status)

    def test_bdf3(self):
        """Newtest17-256 read specific channels only"""

        dat1 = BDF("Newtest17-256.bdf")
        dat2 = BDF("Newtest17-256.bdf", chans=[1, 3, 5])
        dat3 = BDF("Newtest17-256.bdf", chans=["A3"])

        self.assertEqual(np.shape(dat2.data), (3, 15360))
        self.assertEqual(np.shape(dat3.data), (1, 15360))

        self.assertTrue(np.array_equal(dat1.data[0, :],
                                       dat2.data[0, :]))

        self.assertTrue(np.array_equal(dat1.data[2, :],
                                       dat3.data[0, :]))

        self.assertTrue(np.array_equal(dat1.data[2, :],
                                       dat2.data[1, :]))

        self.assertTrue(np.array_equal(dat1.data[2, :],
                                       dat3.data[0, :]))

        self.assertEqual(dat2.hdr["n_chans"], 4)
        self.assertEqual(dat3.hdr["n_chans"], 2)

        self.assertEqual(dat2.hdr["labels"][0], "A1")
        self.assertEqual(dat2.hdr["labels"][1], "A3")
        self.assertEqual(dat3.hdr["labels"][0], "A3")

        self.assertEqual(dat2.hdr["n_recs"], 60)
        self.assertEqual(dat3.hdr["n_recs"], 60)

        self.assertEqual(dat2.hdr["freq"][0], 256)
        self.assertEqual(dat3.hdr["freq"][0], 256)

    def test_bdf4(self):
        """Newtest17-2048 read"""

        dat = BDF("Newtest17-2048.bdf")

        self.assertEqual(dat.hdr["n_bytes_hdr"], 18*256)
        self.assertEqual(dat.hdr["n_chans"], 17)
        self.assertEqual(dat.hdr["n_recs"], 60)
        self.assertEqual(dat.hdr["freq"][0], 2048)
        self.assertEqual(np.shape(dat.data), (16, 122880))
        self.assertEqual(dat.trig["idx"][0], 3352)
        self.assertEqual(dat.trig["val"][0], 255)
        self.assertEqual(dat.trig["count"][255], 39)

    def test_bdf5(self):
        """Newtest17-2048 read header only"""

        dat = BDF("Newtest17-2048.bdf", hdr_only=True)

        self.assertEqual(dat.hdr["n_bytes_hdr"], 18*256)
        self.assertEqual(dat.hdr["n_chans"], 17)
        self.assertEqual(dat.hdr["n_recs"], 60)
        self.assertEqual(dat.hdr["freq"][0], 2048)
        self.assertIsNone(dat.data)
        self.assertIsNone(dat.trig)
        self.assertIsNone(dat.status)

    def test_bdf6(self):
        """Newtest17-2048 read specific channels only"""

        dat1 = BDF("Newtest17-2048.bdf")
        dat2 = BDF("Newtest17-2048.bdf", chans=[1, 3, 5])
        dat3 = BDF("Newtest17-2048.bdf", chans=["A3"])

        self.assertEqual(np.shape(dat2.data), (3, 122880))
        self.assertEqual(np.shape(dat3.data), (1, 122880))

        self.assertTrue(np.array_equal(dat1.data[0, :],
                                       dat2.data[0, :]))

        self.assertTrue(np.array_equal(dat1.data[2, :],
                                       dat3.data[0, :]))

        self.assertTrue(np.array_equal(dat1.data[2, :],
                                       dat2.data[1, :]))

        self.assertTrue(np.array_equal(dat1.data[2, :],
                                       dat3.data[0, :]))

        self.assertEqual(dat2.hdr["n_chans"], 4)
        self.assertEqual(dat3.hdr["n_chans"], 2)

        self.assertEqual(dat2.hdr["n_recs"], 60)
        self.assertEqual(dat3.hdr["n_recs"], 60)

        self.assertEqual(dat2.hdr["freq"][0], 2048)
        self.assertEqual(dat3.hdr["freq"][0], 2048)
