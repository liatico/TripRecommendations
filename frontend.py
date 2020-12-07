import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from mybackend import Database

# int bigger than 0
def isValidNumber(text):
    try:
        return int(text) > 0
    except:
        return False



class MainGrid(GridLayout):

    location: ObjectProperty(None)
    duration: ObjectProperty(None)
    recommendations: ObjectProperty(None)
    sort_Location: ObjectProperty(None)
    sort_Duration: ObjectProperty(None)
    sort_Recommendations: ObjectProperty(None)
    submit: ObjectProperty(None)
    reset: ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainGrid, self).__init__(**kwargs)
        self.container = GridLayout()
        self.submit.bind(on_press=self.submitPressed)
        self.reset.bind(on_press=self.resetPressed)
        self.sort_Location.bind(on_press=self.changeToggleButtonColor)
        self.sort_Duration.bind(on_press=self.changeToggleButtonColor)
        self.sort_Recommendations.bind(on_press=self.changeToggleButtonColor)

        self.toggle_on_color = (20/255,85/255,190/255, 1.0)
        self.toggle_off_color = (225/255, 225/255, 250/255, 0.6)

        self.toggle_on_text_color = (1,1,1,1)
        self.toggle_off_text_color = (0,0,0,1)

        self.popup_sep_color = (15/255, 60/255, 135/255, 1.0)

        self.db = Database()

    def resetPressed(self, instance):
        self.location.text = ""
        self.duration.text = ""
        self.recommendations.text = ""
        self.sort_Location.state="normal"
        self.sort_Duration.state="normal"
        self.sort_Recommendations.state="normal"

        self.sort_Location.background_color = self.toggle_off_color
        self.sort_Duration.background_color = self.toggle_off_color
        self.sort_Recommendations.background_color = self.toggle_off_color
        self.sort_Location.color = self.toggle_off_text_color
        self.sort_Duration.color = self.toggle_off_text_color
        self.sort_Recommendations.color = self.toggle_off_text_color

    def changeToggleButtonColor(self, instance):

        if instance.text == "Location":
            self.sort_Location.background_color = self.toggle_on_color
            self.sort_Duration.background_color = self.toggle_off_color
            self.sort_Recommendations.background_color = self.toggle_off_color
            self.sort_Location.color = self.toggle_on_text_color
            self.sort_Duration.color = self.toggle_off_text_color
            self.sort_Recommendations.color = self.toggle_off_text_color

        elif instance.text == "Duration":
            self.sort_Location.background_color = self.toggle_off_color
            self.sort_Duration.background_color = self.toggle_on_color
            self.sort_Recommendations.background_color = self.toggle_off_color
            self.sort_Location.color = self.toggle_off_text_color
            self.sort_Duration.color = self.toggle_on_text_color
            self.sort_Recommendations.color = self.toggle_off_text_color

        elif instance.text == "Recommendations":
            self.sort_Location.background_color = self.toggle_off_color
            self.sort_Duration.background_color = self.toggle_off_color
            self.sort_Recommendations.background_color = self.toggle_on_color
            self.sort_Location.color = self.toggle_off_text_color
            self.sort_Duration.color = self.toggle_off_text_color
            self.sort_Recommendations.color = self.toggle_on_text_color

    def submitPressed(self, instance):

        loc_text = self.location.text
        dur_text = self.duration.text
        rec_text = self.recommendations.text

        if loc_text == "":
            self.popup_error(instance, "Error", "Location field is empty")
        elif dur_text == "":
            self.popup_error(instance, "Error", "Duration field is empty")
        elif rec_text == "":
            self.popup_error(instance, "Error", "Amount of Recommendations field is empty")
        elif not isValidNumber(dur_text):
            self.popup_error(instance, "Error", "Duration field is invalid (Integer bigger than zero)")
        elif not isValidNumber(rec_text):
            self.popup_error(instance, "Error", "Amount of Recommendations field is invalid (Integer bigger than zero)")
        else:

            print("Location: " + self.location.text)
            print("Duration: " + self.duration.text)
            print("Amount of recommendations: " + self.recommendations.text)
            if self.sort_Location.state == "down":
                self.sortedBy = "Location"
            elif self.sort_Duration.state == "down":
                self.sortedBy = "Duration"
            elif self.sort_Recommendations.state == "down":
                self.sortedBy = "Recommendations"
            else:
                self.sortedBy = "Unsorted"

            print("Sort by: " + self.sortedBy)

            results = self.db.search(loc_text, int(dur_text), int(rec_text), True)
            self.popup_content(instance, results)

    def popup_error(self, obj, title, content, popup_size=500):
        box_popup = BoxLayout(orientation='vertical')
        inner_box_popup = BoxLayout(orientation='horizontal', size_hint_y=None, height=0.7 * popup_size)

        popup = Popup(title=title, title_align="center", title_size=28, separator_color=self.popup_sep_color, background_color=(0,0,0,1), content=box_popup, size_hint_y=None, height=popup_size, size_hint_x=None, width=popup_size)

        inner_box_popup.add_widget(Label(text=content))
        closeBtn = Button(text="X")
        closeBtn.bind(on_press=popup.dismiss)
        closeBtn.background_color = (15/255, 60/255, 135/255, 1.0)
        closeBtn.font_size = 24
        closeBtn.bold = True
        box_popup.add_widget(inner_box_popup)
        box_popup.add_widget(closeBtn)

        popup.open()


    def popup_content(self, obj, content, popup_size=500):
        box_popup = BoxLayout(orientation='vertical')
        inner_box_popup = BoxLayout(orientation='vertical', size_hint_y=None, height=0.7 * popup_size)
        title = "Results"
        inner_box_popup.cols = 3
        if self.sortedBy == "Location":
            title += " sorted by Location"
        elif self.sortedBy == "Duration":
            title += " sorted by Duration"
        elif self.sortedBy == "Recommendations":
            title += " sorted by Recommendations"

        popup = Popup(title=title, title_align="center", title_color=(0,0,0,1), title_size=28, separator_color=self.popup_sep_color, background='popup_background.jpg', content=box_popup, size_hint_y=None, height=popup_size, size_hint_x=None, width=popup_size)

        titles_box = BoxLayout(orientation='horizontal')
        titles_box.add_widget(Label(text="Destination", color=(0,0,0,1), bold=True))
        titles_box.add_widget(Label(text="Duration", color=(0,0,0,1), bold=True))
        titles_box.add_widget(Label(text="Recommendations", color=(0,0,0,1), bold=True))


        inner_box_popup.add_widget(titles_box)

        #content should replace aa, bb, cc
        for res in content:
            dest = res[0]
            dur = res[1][0]
            rec = res[1][1]

            res_box = BoxLayout(orientation='horizontal', spacing=15)
            res_box.add_widget(Label(text=str(dest), color=(0, 0, 0, 1)))
            res_box.add_widget(Label(text=str(dur), color=(0, 0, 0, 1)))
            res_box.add_widget(Label(text=str(rec), color=(0, 0, 0, 1)))
            inner_box_popup.add_widget(res_box)

        #inner_box_popup.add_widget(Label(text=content, color=(0,0,0,1)))
        closeBtn = Button(text="X")
        closeBtn.bind(on_press=popup.dismiss)
        closeBtn.background_color = (15/255, 60/255, 135/255, 1.0)
        closeBtn.font_size = 24
        closeBtn.bold = True
        box_popup.add_widget(inner_box_popup)
        box_popup.add_widget(closeBtn)

        popup.open()



class MyApp(App):
    def build(self):
        self.title = 'RecoTravel'
        Window.clearcolor = (180/255, 220/255, 215/255, 1)

        return MainGrid()


if __name__ == "__main__":
    MyApp().run()
