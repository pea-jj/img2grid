import jinja2
import os

class Render:
     def __init__(self, folder, out_folder, schema):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(folder))
        files = os.listdir(folder)
        for file in files:
            if not os.path.isdir(file):
                temp = env.get_template(file)
                temp_out = temp.render(schema=schema)
                with open(os.path.join(out_folder, file), 'w', encoding='utf-8') as f:
                    f.write(temp_out)
        

       