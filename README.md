# gmymaps

## Impetus
Google Maps has a convenient feature for saving points of interest, called My Maps. Such maps are
useful for sharing locations with friends. Unfortunately, Google does not provide an API to
programatically view or update a MyMaps map<sup>[1](#references)</sup>, and it is
unlikely to be available any time soon.

This package acts as a simple wrapper around the endpoints used by the official My Maps web app,
essentially mimicking the web app's behavior.


## Try it out!
1. Head over to [My Maps](https://www.google.com/maps/d/u/0/) and create a My Maps map.
2. On [Google Drive](https://drive.google.com/drive), make the map publicly accessible by sharing
it as link for anyone to edit.

**Fetching map data**
```python
import gmymaps

map_id = 'your-map-id-here'
client = gmymaps.get_client()
result = client.get_map_data(map_id)
```

**Editing points and layers**
```python
from gmymaps import PointAttrs, PointAttrType

map_id = 'your-map-id-here'
layer_id = client.create_layer(map_id)
client.update_layer(map_id, layer_id, layer_name='My New Layer')

point_id = client.create_point(map_id, layer_id)
attrs = (PointAttrs()
    .add_attr(PointAttrType.NAME, "My New Point")
    .add_attr(PointAttrType.DESCRIPTION, "This is an interesting place to go!")
    .add_attr(PointAttrType.COORD, [1.37, 103.75]))
client.update_point(map_id, layer_id, point_id, attrs)

client.delete_point(map_id, layer_id, point_id)
client.delete_layer(map_id, layer_id)
```

## Cookies
When attempting to access a private map, requests will be redirected to a sign-in page.
This redirection occurs even if the map is shared with a service account and
accessed using OAuth credentials from that account. To bypass this, you can save a session cookie,
similar to yt-dlp's `--cookies-from-browser` feature. For more details, refer to `cookie.py`.


## Future work
- Creating convenience wrappers like `Map` and `Layer`
- Changing of point colors
- Uploading and downloading of KML files


## References
1: Link to issue: https://issuetracker.google.com/issues/35820262
