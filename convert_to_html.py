# # html output

          # wrapper = """
          #           <html>
          #           <header>
          #           Recipe: Non Vegetarian Transformation
          #           </header>
          #           <body>
          #           <title> Ingredients </title>
          #                {{htmlText}}
          #           </body>
          #           </html>
          #           """

          # file_loader = FileSystemLoader('templates')
          # env = Environment(loader=file_loader)

          # htmlLines = ["<ul>"]
          # for ingredient in ingredients:
          #      textLine = ingredient.text
          #      htmlLines.append('<li>%s</li>' % textLine) # or something even nicer
          # htmlLines.append("</ul>")
          # htmlText = '\n'.join(htmlLines)

          # with open("templates/ingredients.txt",'w') as f:
          #      f.write(wrapper)
          


          # template = env.get_template("ingredients.txt")
          # output = template.render(htmlText = htmlText)
          
          # with open("ingredients.html",'w') as f:
          #      f.write(output)