library(shiny)
library(DT)

shinyUI(tagList(fluidPage(theme = "bootstrap.css",
                          includeScript("./text.js"),
                          titlePanel("Folder content upload"),
                          
                          fluidRow(
                            column(4,
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
                            column(8,
                                   tabsetPanel(
                                     tabPanel("Files table", dataTableOutput("tbl")),
                                     tabPanel("Files list", dataTableOutput("tbl2"))
                                   )
                            )
                          )
),
HTML("<script type='text/javascript' src='getFolders.js'></script>")
)

) 