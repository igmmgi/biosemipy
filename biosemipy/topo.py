""" EEG Topographic Plots """

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Wedge
import matplotlib.animation as animation
from scipy.spatial import ConvexHull
from scipy.interpolate import Rbf


class Topo:
    """EEG Topographic Plots"""

    def __init__(
        self,
        layout_file="biosemi64.csv",
        z_scale=None,
        colormap="jet",
        labels=True,
        labels_kwargs={},
        markers=True,
        markers_kwargs={},
        roi_outline=False,
        roi_outline_kwargs={},
        title=True,
        title_kwargs={},
    ):

        self.read_layout(layout_file)
        self.outline = self.generate_outline()
        self.z_scale = z_scale
        self.colormap = colormap
        self.labels = labels
        self.labels_kwargs = labels_kwargs
        self.markers = markers
        self.markers_kwargs = markers_kwargs
        self.roi_outline = roi_outline
        self.roi_outline_kwargs = roi_outline_kwargs
        self.title = title
        self.title_kwargs = title_kwargs

        self.fills = None
        self.lines = None
        self.fig = plt.figure()
        self.ax = plt.gca()
        self.cb = None

        self._setup()

    def _setup(self):

        plt.axis("equal")
        plt.axis("off")
        plt.xlim(-1.15, 1.15)
        plt.ylim(-1.15, 1.15)

        # draw head shape
        for item in self.outline.values():
            self.ax.add_patch(item)

        if self.markers:
            self.plot_markers(**self.markers_kwargs)

        if self.labels:
            self.plot_labels(**self.labels_kwargs)

        if self.roi_outline:
            self.draw_roi_outline(**self.roi_outline_kwargs)

        if self.title:
            self.plot_title(**self.title_kwargs)

    def generate_outline(self, linewidth=2):
        """Generate head, nose, and ear outlines for plot."""

        head = Circle(
            xy=[0, 0],
            radius=1,
            linewidth=linewidth,
            edgecolor="k",
            facecolor="white",
            zorder=0,
        )

        nose = Wedge(
            [0, 1.15],
            0.25,
            250,
            290,
            linewidth=linewidth,
            edgecolor="k",
            facecolor="w",
            zorder=-1,
        )

        l_ear = Ellipse(
            xy=[-1, 0],
            width=0.2,
            height=0.5,
            linewidth=linewidth,
            edgecolor="k",
            facecolor="w",
            zorder=-1,
        )

        r_ear = Ellipse(
            xy=[1, 0],
            width=0.2,
            height=0.5,
            linewidth=linewidth,
            edgecolor="k",
            facecolor="w",
            zorder=-1,
        )

        return {"head": head, "nose": nose, "l_ear": l_ear, "r_ear": r_ear}

    def read_layout(self, layout_name, fit_coords=True):
        """Read BioSemi position coordinate file."""

        layout_name = os.path.join(os.path.dirname(__file__), "layouts", layout_name)
        self.layout = pd.read_csv(layout_name)
        self._polar2cart_coordinates()
        if fit_coords:
            self._fit_coords_to_head()

    def _polar2cart_coordinates(self):
        """
        Convert original BioSemi polar coordinates to x, y positions
        with the nose to the top of the plot.
        """

        inc = self.layout["inc"] * (np.pi / 180)
        azi = self.layout["azi"] * (np.pi / 180)

        self.layout["x"] = inc * np.cos(azi)
        self.layout["y"] = inc * np.sin(azi)

    def _fit_coords_to_head(self):
        """Fit coordinates inside head circumference."""

        x, y = self.layout["x"], self.layout["y"]
        while np.any(np.sqrt(x**2 + y**2) > 1):
            x *= 0.99
            y *= 0.99

        self.layout["x"] = x
        self.layout["y"] = y

    def interp_data(self, data, res=100):
        """Interperet data using scipy.interpolate.Rbf."""

        interp = Rbf(self.layout["x"], self.layout["y"], data, function="cubic")

        # x, y points slightly beyond head circumference
        x, y = np.meshgrid(np.linspace(-1.05, 1.05, res), np.linspace(1.05, -1.05, res))

        self.data = x, y, interp(x, y)

    def draw_roi_outline(self, rois=None, color="black", border_size=0.1):

        # points forming a circle
        border_points = np.arange(0, 2 * np.pi + np.pi / 30, 2 * np.pi / 30)
        border_x = np.sin(border_points) * border_size
        border_y = np.cos(border_points) * border_size

        # labels and channel positions
        labels = self.layout["label"]
        pos_x = np.array(self.layout["x"])
        pos_y = np.array(self.layout["y"])

        for idx, roi in enumerate(rois):
            roi_pos_x = np.array([])
            roi_pos_y = np.array([])
            for point in zip(labels, pos_x, pos_y):
                if roi is not None and point[0] not in roi:
                    continue
                roi_pos_x = np.hstack([roi_pos_x, border_x + point[1]])
                roi_pos_y = np.hstack([roi_pos_y, border_y + point[2]])

            roi_border = ConvexHull(np.stack([roi_pos_x, roi_pos_y]).T)
            for border in roi_border.simplices:
                plt.plot(roi_pos_x[border], roi_pos_y[border], color[idx], zorder=3)

    def plot_markers(self, **kwargs):
        """
        Plot markers at x, y 2D coordinates on topo-plot.
        For kwargs, see matplotlib.pyplot.scatter
        """

        # set some defaults
        if "s" not in kwargs:
            kwargs["s"] = 2
        if "c" not in kwargs:
            kwargs["c"] = "black"

        plt.scatter(self.layout["x"], self.layout["y"], zorder=3, **kwargs)

    def plot_labels(self, **kwargs):
        """
        Plot labels at x, y 2D coordinates on topo-plot.
        For kwargs, see matplotlib.pyplot.annotate
        Additional kwargs:
            labels: str
            labels_offset: (0, 0)
        """

        # additional kwargs defaults
        labels = list(self.layout["label"])
        labels_offset = (0, 0)
        if "labels" in kwargs:
            labels = kwargs["labels"]
            kwargs.pop("labels")
        if "labels_offset" in kwargs:
            labels_offset = kwargs["labels_offset"]
            kwargs.pop("labels_offset")

        for _, row in self.layout.iterrows():
            if row["label"] in labels:
                x = row["x"] + labels_offset[0]
                y = row["y"] + labels_offset[1]
                plt.annotate(row["label"], (x, y), zorder=3, **kwargs)

    def plot_colorbar(self, **kwargs):
        """
        Plot colorbar.
        For kwargs see matplotlib.pyplot.colorbar.
        Additional kwargs:
            label: str
            colorbar_pos: list
        """
        # additional kwargs defaults
        label = "Amplitude ($\mu$V)"
        if "label" in kwargs:
            label = kwargs["label"]
            kwargs.pop("label")

        colorbar_pos = None
        for key in kwargs:
            if key == colorbar_pos:
                colorbar_pos = kwargs[key]

        cbar_ax = None
        if colorbar_pos is not None:
            cbar_ax = self.fig.add_subplot(colorbar_pos)

        self.cb = self.fig.colorbar(self.fills, cax=cbar_ax, **kwargs)
        self.cb.set_label(label, rotation=-90)

    def plot_contour_lines(self, **kwargs):

        # some default kwargs to plt.contour
        if "levels" not in kwargs:
            kwargs["levels"] = 10
        if "colors" not in kwargs:
            kwargs["colors"] = "grey"

        # remove old contour is updating data
        if self.lines is not None:
            for line in self.lines.collections:
                line.remove()

        self.lines = plt.contour(
            self.data[0], self.data[1], self.data[2], zorder=3, **kwargs
        )

        for line in self.lines.collections:
            line.set_clip_path(self.outline["head"])

    def plot_title(self, **kwargs):

        title = ""
        if "title" in kwargs:
            title = kwargs["title"]
            kwargs.pop("title")
        xy = (0, 1.15)
        if "xy" in kwargs:
            xy = kwargs["xy"]
            kwargs.pop("xy")
        if "fontsize" not in kwargs:
            kwargs["fontsize"] = 18

        self.ax.annotate(title, xy=xy, ha="center", **kwargs)

    def plot(
        self,
        data,
        z_scale=None,
        contour_lines=True,
        colorbar=True,
        colorbar_kwargs={},
        contour_lines_kwargs={},
    ):

        # interpolate and plot
        self.interp_data(data)
        if z_scale is not None:
            z_scale = np.linspace(z_scale[0], z_scale[1], z_scale[2])

        self.fills = plt.contourf(
            self.data[0],
            self.data[1],
            self.data[2],
            levels=z_scale,
            cmap="jet",
            extend="both",
            zorder=1,
        )
        for fill in self.fills.collections:
            fill.set_clip_path(self.outline["head"])

        if colorbar and self.cb is None:
            self.plot_colorbar(**colorbar_kwargs)

        if contour_lines:
            self.plot_contour_lines(**contour_lines_kwargs)

    def show(self):
        plt.ion()
        plt.pause(0.001)
        plt.show()


def run_examples():

    # Example 1
    topo = Topo()
    topo.show()

    # Example 2
    topo = Topo()
    topo.plot(data=np.random.randn(64) * 10)
    topo.show()

    # Example 3
    topo = Topo()
    topo.plot(data=np.random.randn(64), contour_lines=True)
    topo.show()

    # Example 4
    topo = Topo(layout_file="biosemi256.csv")
    topo.plot(data=np.random.randn(256) * 10)
    topo.show()

    # Example 5
    topo = Topo(
        roi_outline=True,
        roi_outline_kwargs={
            "rois": [
                ["Cz", "C1", "C2"],
                ["PO7", "P7"],
                ["PO8", "P8"],
                ["Fp1", "Fp2", "FpZ"],
            ],
            "color": ["black", "blue", "blue", "red"],
        },
    )
    topo.show()


if __name__ == "__main__":
    run_examples()
