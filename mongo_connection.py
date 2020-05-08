import pymongo
import urllib
import re

# Connects to MongoDB instance and then inserts or gets all the values in the
# table Mongo has
class Connector:
    def insert_workout(self, workout_name, workout_link):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.exercise_database
        print("connected to database")
        regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
        match = regex.match(urllib.parse.unquote(workout_link))
        if not match:
            print("Given link {0} does not match the regular expression".format(workout_link))
            return
        video_id = match.group("id")
        workout_item = {"workout_name": workout_name, "workout_link": video_id}
        print("attempting to insert {0} {1}".format(workout_name, video_id, "utf-8"))
        x = db.exercises.insert_one(workout_item).inserted_id
        print("inserted the item {0}".format(x))
        return

    # return all the workout values
    def get_workouts(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.exercise_database
        html_output = ""
        for workout_item in db.exercises.find():
            html_output = html_output + "<tr>\n<td>" + workout_item['workout_name'] + "</td>\n<td>"
            html_output = html_output + "<a href=\"javascript:changeVideo(\'" + \
                          urllib.parse.unquote(workout_item['workout_link']) + \
                          "\');\">Click to open video</a>" \
                          + "</td>\n"
            html_output = html_output + "</tr>\n"
        return html_output
