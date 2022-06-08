# # html output

from jinja2 import Environment, FileSystemLoader

def template(steps, ingredients, stepsNew, ingredientsNew, t):
     wrapper = """
               <html>
                    <style>
                    table, th, td {
                    border: 1px solid white;
                    border-radius: 4px;
                    border-collapse: collapse
                    }
                    th, td {
                    background-color: #96D4D4;
                    padding: 7px
                    }
                    </style>
                    <body>

                    <h2>Ingredient Comparison</h2>

                    <table style="width:100%">
                    <tr>
                    <th>Before Transformation</th>
                    <th>After Transformation</th>
                    </tr>
                    <tr>
                    <td>{{ingredientsBefore}}</td>
                    <td>{{ingredientsAfter}}</td>
                    </tr>
                    </table>

                    <h2>Instructions Comparison</h2>

                    <table style="width:100%">
                    <tr>
                    <th>Before Transformation</th>
                    <th>After Transformation</th>
                    </tr>
                    <tr>
                    <td>{{stepsBefore}}</td>
                    <td>{{stepsAfter}}</td>
                    </tr>
                    </table>

                    </body>
                    </html>


               """

     file_loader = FileSystemLoader('templates')
     env = Environment(loader=file_loader)

     htmlLines = ["<ol>"]
     for step in steps:
          textLine = step
          htmlLines.append('<li>%s</li>' % textLine) # or something even nicer
     htmlLines.append("</ol>")
     stepsBefore = '\n'.join(htmlLines)

     htmlLines = ["<ol>"]
     for step in stepsNew:
          textLine = step
          htmlLines.append('<li>%s</li>' % textLine) # or something even nicer
     htmlLines.append("</ol>")
     stepsAfter = '\n'.join(htmlLines)

     htmlLines = ["<ol>"]
     for ingredient in ingredients:
          textLine = ingredient
          htmlLines.append('<li>%s</li>' % textLine) # or something even nicer
     htmlLines.append("</ol>")
     ingredientsBefore = '\n'.join(htmlLines)

     htmlLines = ["<ol>"]
     for ingredient in ingredientsNew:
          textLine = ingredient
          htmlLines.append('<li>%s</li>' % textLine) # or something even nicer
     htmlLines.append("</ol>")
     ingredientsAfter = '\n'.join(htmlLines)

     with open("templates/template.txt",'w') as f:
          f.write(wrapper)
     


     template = env.get_template("template.txt")
     output = template.render(stepsBefore = stepsBefore, stepsAfter = stepsAfter, ingredientsBefore = ingredientsBefore, ingredientsAfter = ingredientsAfter)
     
     with open(f"{t}.html",'w', encoding='utf-8') as f:
          f.write(output)