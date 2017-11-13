import settings
import math
import requests


def coord_distance(lat1, lon1, lat2, lon2):
    """
    Finds the distance between two pairs of latitude and longitude.
    :param lat1: Point 1 latitude.
    :param lon1: Point 1 longitude.
    :param lat2: Point two latitude.
    :param lon2: Point two longitude.
    :return: Kilometer distance.
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    km = 6367 * c
    return km


def in_box(coords, box):
    """
    Find if a coordinate tuple is inside a bounding box.
    :param coords: Tuple containing latitude and longitude.
    :param box: Two tuples, where first is the bottom left, and the second is the top right of the box.
    :return: Boolean indicating if the coordinates are in the box.
    """
    if box[0][0] < coords[0] < box[1][0] and box[1][1] < coords[1] < box[0][1]:
        return True
    return False


def post_listing_to_slack(sc, listing):
    """
    Posts the listing to slack.
    :param sc: A slack client.
    :param listing: A record of the listing.
    """
    commute_time = None
    if listing["commute_time"] is not None:
        commute_time = round(listing["commute_time"] / 60)

    desc = "{0} | *{1}* | {2} | {3} | <{4}> | <{5}>".format(listing["area"],
                                                                  listing["price"],
                                                                  commute_time,
                                                                  listing["name"],
                                                                  listing['google_link'],
                                                                  listing["url"])
    sc.api_call(
        "chat.postMessage", channel=settings.SLACK_CHANNEL, text=desc,
        username='pybot', icon_emoji=':robot_face:'
    )


def find_points_of_interest(geotag, location):
    """
    Find points of interest, like transit, near a result.
    :param geotag: The geotag field of a Craigslist result.
    :param location: The where field of a Craigslist result.  Is a string containing a description of where
    the listing was posted.
    :return: A dictionary containing annotations.
    """
    area_found = False
    area = ""
    # min_dist = None
    # near_bart = False
    # bart_dist = "N/A"
    # bart = ""
    # Look to see if the listing is in any of the neighborhood boxes we defined.
    for a, coords in settings.BOXES.items():
        if in_box(geotag, coords):
            area = a
            area_found = True

    # Check to see if the listing is near any transit stations.
    # for station, coords in settings.TRANSIT_STATIONS.items():
    #     dist = coord_distance(coords[0], coords[1], geotag[0], geotag[1])
    #     if (min_dist is None or dist < min_dist) and dist < settings.MAX_TRANSIT_DIST:
    #         bart = station
    #         near_bart = True
    #
    #     if (min_dist is None or dist < min_dist):
    #         bart_dist = dist

    # If the listing isn't in any of the boxes we defined, check to see if the string description of the neighborhood
    # matches anything in our list of neighborhoods.
    if len(area) == 0:
        for hood in settings.NEIGHBORHOODS:
            if hood in location.lower():
                area = hood

    commute_time = compute_transit_distance(geotag)
    google_link = 'http://www.google.com/maps/place/{},{}'.format(geotag[0], geotag[1])

    return {
        "area_found": area_found,
        "area": area,
        # "near_bart": near_bart,
        # "bart_dist": bart_dist,
        # "bart": bart,
        "commute_time": commute_time,
        "google_link": google_link
    }


def compute_transit_distance(geotag):
    office = settings.OFFICE
    url = 'https://maps.googleapis.com/maps/api/directions/json?' \
          'origin={},{}' \
          '&destination={},{}' \
          '&mode=transit&key={}'.format(geotag[0], geotag[1], office[0], office[1],
                                        settings.DIRECTIONS_API_KEY)

    response = requests.get(url)
    try:
        commute_time = response.json()["routes"][0]["legs"][0]["duration"]["value"]
    except:
        print("Cannot parse the directions data for the location: {}".format(office))
        commute_time = 0

    return commute_time
