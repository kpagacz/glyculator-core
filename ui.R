library (shiny)

shinyUI (tagList(fluidPage(
  includeScript("./text.js"),
  titlePanel("Glyculator v2 alpha"),
  fluidRow(
    numericInput ("idrow", label = "idrow", value = 3),
    numericInput ("idcol", label = "idcol", value = 2),
    numericInput ("perday", label = "perday", value = 288),
    numericInput ("headnrows", label = "headnrows", value = 13),
    numericInput ("datecol", label = "datecol", value = 2),
    numericInput ("timecol", label = "timecol", value = 3),
    numericInput ("dtcol", label = "dtcol", value = 4),
    numericInput ("glucosecol", label = "glucosecol", value = 10),
    textInput ("max days", label = "maxdays", value = "F"),
    textInput ("extension", label = "ext", value = ".csv"),
    textInput ("separator", label = "sep", value = ",")
  ),
  fluidRow(
    wellPanel(
             tags$div(class="form-group shiny-input-container", 
                      tags$div(tags$label("File input")),
                      tags$div(tags$label("Choose folder", class="btn btn-primary",
                                          tags$input(id = "fileIn", webkitdirectory = TRUE, type = "file", style="display: none;", onchange="pressed()"))),
                      tags$label("No folder choosen", id = "noFile"),
                      tags$div(id="fileIn_progress", class="progress progress-striped active shiny-file-input-progress",
                               tags$div(class="progress-bar")
                      )     
             )
    )
  ),
  fluidRow(
    textOutput ("directory")
  )
),
HTML("<script type='text/javascript' src='getFolders.js'></script>")
))