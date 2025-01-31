import json
import numpy as np
import xarray as xr
from pyorc import helpers

class ORCBase(object):
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    @property
    def h_a(self):
        """Actual water level belonging to the processed video

        Returns
        -------
        h : float
            deserialized representation of actual water level
        """
        return json.loads(self._obj.h_a)


    @property
    def camera_config(self):
        """Camera configuration belonging to the processed video

        Returns
        -------
            obj : pyorc.CameraConfig object
        """
        if not(hasattr(self, "_camera_config")):
            #  first set the camera config and shape
            self._set_camera_config()
        return self._camera_config

    @camera_config.setter
    def camera_config(self, cam_config):
        if isinstance(cam_config, str):
            # convert into a camera_config object
            from pyorc import get_camera_config
            self._camera_config = get_camera_config(cam_config)
        else:
            self._camera_config = cam_config

    @property
    def camera_shape(self):
        """Shape of the original camera objective of the processed video (e.g. 1080, 1920)

        Returns
        -------
        r : int
            number of rows
        c : int
            number of columns
        """
        return self._camera_shape

    @camera_shape.setter
    def camera_shape(self, cam_shape):
        if isinstance(cam_shape, str):
            self._camera_shape = helpers.deserialize_attr(self._obj, "camera_shape", np.array)
        else:
            self._camera_shape = self._obj.camera_shape

    def _set_camera_config(self):
        # set the camera config
        self.camera_config = self._obj.camera_config
        self.camera_shape = self._obj.camera_shape


    def _add_xy_coords(
        self,
        xy_coord_data,
        coords,
        attrs_dict
    ):
        """Add coordinate variables with x and y dimensions (2d) to existing xr.Dataset.

        Parameters
        ----------
        xy_coord_data: list
            one or several arrays with 2-dimensional coordinates
        coords: tuple of str
            the dimensions belonging to the data in xy_coord_data
        attrs_dict: list of dict
            attributes belonging to xy_coord_data, must have equal length as xy_coord_data.

        Returns
        -------
        ds : xr.Dataset
            same as input, but with added coordinate variables.
        """
        dims = tuple(coords.keys())
        xy_coord_data = [
            xr.DataArray(
                data,
                dims=dims,
                coords=coords,
                attrs=attrs,
                name=name
            ) for data, (name, attrs) in zip(xy_coord_data, attrs_dict.items()) if data is not None]
        # assign the coordinates
        frames_coord = self._obj.assign_coords({
            k: (dims, v.values) for k, v in zip(attrs_dict, xy_coord_data)
        })
        # add the attributes (not possible with assign_coords
        for k, v in zip(attrs_dict, xy_coord_data):
            frames_coord[k].attrs = v.attrs
        # update the DataArray
        return frames_coord

