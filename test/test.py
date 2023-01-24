import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("My Application")

        grid  = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)

        label = Gtk.Label()
        label.set_markup("Select Layout")

        for i in range(2):
            grid.insert_column(i)
            grid.insert_row(i)    
      
       
        image_files = {
            "set1":"set1.svg",
            "set2":"set2.svg",
            "set3":"set3.svg",
            "set4":"set4.svg"
        }
                   
            
        grid.attach(label,0,0,2,1)

        grid.attach(self.create_button_with_image(image_files["set1"],"set1",self.on_click), 0, 1, 1, 1)
        grid.attach(self.create_button_with_image(image_files["set2"],"set2",self.on_click), 1, 1, 1, 1)
        grid.attach(self.create_button_with_image(image_files["set3"],"set3",self.on_click), 0, 2, 1, 1)
        grid.attach(self.create_button_with_image(image_files["set4"],"set4",self.on_click), 1, 2, 1, 1)

        window.set_child(grid)     
        window.show()

    def on_click(self,action):
        print("clicked : %s"%action.get_name())


    def create_button_with_image(self,img_path:str,name:str,function):
        btn = Gtk.Button()
        img = Gtk.Image()
        img.set_from_file(img_path)
        img.set_size_request(200,200)
        btn.set_child(img)
        btn.connect("clicked",function)
        btn.set_name(name)
        return btn


app = MyApplication()
app.run(None)
