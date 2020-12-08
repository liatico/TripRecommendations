import random

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

from kivy.properties import ObjectProperty
from mybackend import Database


# int bigger than 0
def is_valid_number(text):
    try:
        return int(text) > 0
    except:
        return False


class MainGrid(GridLayout):

    # kv properties
    location: ObjectProperty(None)
    duration: ObjectProperty(None)
    recommendations: ObjectProperty(None)
    sort_Location: ObjectProperty(None)
    sort_Duration: ObjectProperty(None)
    sort_Recommendations: ObjectProperty(None)
    submit: ObjectProperty(None)
    reset: ObjectProperty(None)
    last_search: ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainGrid, self).__init__(**kwargs)

        self.container = GridLayout()

        # buttons bindings
        self.submit.bind(on_press=self.submit_pressed)
        self.reset.bind(on_press=self.reset_pressed)
        self.last_search.bind(on_press=self.last_search_pressed)
        self.sort_Location.bind(on_press=self.change_toggle_button_color)
        self.sort_Duration.bind(on_press=self.change_toggle_button_color)
        self.sort_Recommendations.bind(on_press=self.change_toggle_button_color)

        # buttons and popup colors
        self.toggle_on_color = (20/255, 85/255, 190/255, 1.0)
        self.toggle_off_color = (225/255, 225/255, 250/255, 0.6)
        self.toggle_on_text_color = (1, 1, 1, 1)
        self.toggle_off_text_color = (0, 0, 0, 1)
        self.popup_sep_color = (15/255, 60/255, 135/255, 1.0)

        # initial sort type
        self.sortedBy = "Unsorted"

        # Max results shown in each popup
        self.max_results_in_popup = 10

        # db object
        self.db = Database()

        self.last_search_location = ""
        self.last_search_duration = ""
        self.last_search_recommendations = ""

    def last_search_pressed(self, instance):
        self.location.text = self.last_search_location
        self.duration.text = self.last_search_duration
        self.recommendations.text = self.last_search_recommendations


    # Reset button pressed
    def reset_pressed(self, instance):
        # Texts initiations
        self.location.text = ""
        self.duration.text = ""
        self.recommendations.text = ""
        self.sort_Location.state = "normal"
        self.sort_Duration.state = "normal"
        self.sort_Recommendations.state = "normal"

        # Colors initiations
        self.sort_Location.background_color = self.toggle_off_color
        self.sort_Duration.background_color = self.toggle_off_color
        self.sort_Recommendations.background_color = self.toggle_off_color
        self.sort_Location.color = self.toggle_off_text_color
        self.sort_Duration.color = self.toggle_off_text_color
        self.sort_Recommendations.color = self.toggle_off_text_color

    # Change toggle buttons color
    def change_toggle_button_color(self, instance):

        # Location sort button
        if instance.text == "Location":
            # background
            self.sort_Location.background_color = self.toggle_on_color
            self.sort_Duration.background_color = self.toggle_off_color
            self.sort_Recommendations.background_color = self.toggle_off_color
            # font color
            self.sort_Location.color = self.toggle_on_text_color
            self.sort_Duration.color = self.toggle_off_text_color
            self.sort_Recommendations.color = self.toggle_off_text_color

        # Duration sort button
        elif instance.text == "Duration":
            # background
            self.sort_Location.background_color = self.toggle_off_color
            self.sort_Duration.background_color = self.toggle_on_color
            self.sort_Recommendations.background_color = self.toggle_off_color
            # font color
            self.sort_Location.color = self.toggle_off_text_color
            self.sort_Duration.color = self.toggle_on_text_color
            self.sort_Recommendations.color = self.toggle_off_text_color

        # Recommendations sort button
        elif instance.text == "Recommendations":
            # background
            self.sort_Location.background_color = self.toggle_off_color
            self.sort_Duration.background_color = self.toggle_off_color
            self.sort_Recommendations.background_color = self.toggle_on_color
            # font color
            self.sort_Location.color = self.toggle_off_text_color
            self.sort_Duration.color = self.toggle_off_text_color
            self.sort_Recommendations.color = self.toggle_on_text_color

    # Submit button pressed
    def submit_pressed(self, instance):

        # Input from user
        loc_text = self.location.text.strip()
        dur_text = self.duration.text.strip()
        rec_text = self.recommendations.text.strip()

        # Location field empty
        if loc_text == "":
            self.popup_error(instance, "Error", "Location field is empty")
        # Duration field empty
        elif dur_text == "":
            self.popup_error(instance, "Error", "Duration field is empty")
        # Results field empty
        elif rec_text == "":
            self.popup_error(instance, "Error", "Num of Results field is empty")
        # Duration is not a valid number
        elif not is_valid_number(dur_text):
            self.popup_error(instance, "Error", "Duration field is invalid (Integer bigger than zero)")
        # Results is not a valid number
        elif not is_valid_number(rec_text):
            self.popup_error(instance, "Error", "Num of Results field is invalid (Integer bigger than zero)")
        else:

            # Searching for recommendations
            results = self.db.search(loc_text, int(dur_text), int(rec_text), True)

            # Last search
            self.last_search_location = loc_text
            self.last_search_duration = dur_text
            self.last_search_recommendations = rec_text

            # Sort by Location
            if self.sort_Location.state == "down":
                self.sortedBy = "Location"
                results.sort(key=lambda tup: tup[0])

            # Sort by Duration
            elif self.sort_Duration.state == "down":
                self.sortedBy = "Duration"
                results.sort(key=lambda tup: tup[1][0])

            # Sort by Recommendations
            elif self.sort_Recommendations.state == "down":
                self.sortedBy = "Recommendations"
                results.sort(key=lambda tup: tup[1][1], reverse=True)

            # Unsorted
            else:
                self.sortedBy = "Unsorted"
                random.shuffle(results)

            curr_results_list = []
            results_len = len(results)

            # If needed more than 1 popup for results
            if len(results) > self.max_results_in_popup:
                # While there are results left
                while len(results) != 0:
                    curr_results = results[0:self.max_results_in_popup]
                    curr_results_list.insert(0, curr_results)
                    results = results[self.max_results_in_popup:]

                # Shows popup for each group in reversed order
                for res in curr_results_list:
                    results_len = results_len - len(res)
                    # Checks if it is the last popup to change button's text
                    if curr_results_list[0] == res:
                        self.popup_content(instance, res, results_len, "Done")
                    else:
                        self.popup_content(instance, res, results_len, "Next")

            # If needed only one popup
            elif len(results) > 0:
                self.popup_content(instance, results, 0, "Done")

            # No Results found
            else:
                self.popup_error(instance, "Error", "No results founds")

            # Reset fields after submit pressed
            self.reset_pressed(instance)

    # Shows error popup
    def popup_error(self, obj, title, content, popup_size=500):
        # Outer box
        box_popup = BoxLayout(orientation='vertical')
        # Inner box
        inner_box_popup = BoxLayout(orientation='horizontal', size_hint_y=None, height=0.7 * popup_size)

        popup = Popup(title=title, title_align="center", title_size=28, separator_color=self.popup_sep_color, background_color=(0, 0, 0, 1), content=box_popup, size_hint_y=None, height=popup_size, size_hint_x=None, width=popup_size)

        # Content
        inner_box_popup.add_widget(Label(text=content))

        # Close button
        close_btn = Button(text="X")
        close_btn.bind(on_press=popup.dismiss)
        close_btn.background_color = (15/255, 60/255, 135/255, 1.0)
        close_btn.font_size = 24
        close_btn.bold = True

        box_popup.add_widget(inner_box_popup)
        box_popup.add_widget(close_btn)

        popup.open()

    # Content popup
    def popup_content(self, obj, content, index, close_btn_text, popup_size=500):
        # Outer box
        box_popup = BoxLayout(orientation='vertical')
        # Inner box
        inner_box_popup = BoxLayout(orientation='vertical', size_hint_y=None, height=0.7 * popup_size)
        inner_box_popup.cols = 4

        # Change title according to sort type
        title = "Results"
        if self.sortedBy == "Location":
            title += " sorted by Location"
        elif self.sortedBy == "Duration":
            title += " sorted by Duration"
        elif self.sortedBy == "Recommendations":
            title += " sorted by Recommendations"

        popup = Popup(title=title, title_align="center", title_color=(0, 0, 0, 1), title_size=28, separator_color=self.popup_sep_color, background='popup_background.jpg', content=box_popup, size_hint_y=None, height=popup_size, size_hint_x=None, width=popup_size)

        # Titles
        titles_box = BoxLayout(orientation='horizontal')
        titles_box.add_widget(Label(text="ID", color=(0, 0, 0, 1), bold=True))
        titles_box.add_widget(Label(text="Destination", color=(0, 0, 0, 1), bold=True))
        titles_box.add_widget(Label(text="Duration", color=(0, 0, 0, 1), bold=True))
        titles_box.add_widget(Label(text="Recommendations", color=(0, 0, 0, 1), bold=True))
        inner_box_popup.add_widget(titles_box)

        # For each result received
        for res in content:
            # Result parameters
            dest = res[0]
            dur = res[1][0]
            rec = res[1][1]
            index += 1

            # Result box
            res_box = BoxLayout(orientation='horizontal', spacing=15)
            res_box.add_widget(Label(text=str(index), color=(0, 0, 0, 1)))
            res_box.add_widget(Label(text=str(dest), color=(0, 0, 0, 1)))
            res_box.add_widget(Label(text=str(dur), color=(0, 0, 0, 1)))
            res_box.add_widget(Label(text=str(rec), color=(0, 0, 0, 1)))
            inner_box_popup.add_widget(res_box)

        # Close button
        close_btn = Button(text=close_btn_text)
        close_btn.bind(on_press=popup.dismiss)
        close_btn.background_color = (15/255, 60/255, 135/255, 1.0)
        close_btn.font_size = 24
        close_btn.bold = True

        box_popup.add_widget(inner_box_popup)
        box_popup.add_widget(close_btn)

        popup.open()

# Main app
class MyApp(App):
    def build(self):
        self.title = 'RecoTravel'
        Window.clearcolor = (180/255, 220/255, 215/255, 1)

        return MainGrid()


if __name__ == "__main__":
    MyApp().run()
