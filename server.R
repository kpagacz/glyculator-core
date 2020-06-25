if (!require("shiny")) { install.packages("shiny")}
library (shiny)
if (!require("rmarkdown")) { install.packages("rmarkdown")}
library(rmarkdown)

source(paste0(getwd(), "/scripts/calculator.R"))

options(shiny.maxRequestSize=10*1024^2)

shinyServer(function(input, output, session) {
  
# observeEvent reacts to pressing the submit button.
observeEvent(input$button, {
    withProgress(message = "calculation in progress", detail = 'It may take up to a few minutes...',
                 value = 0, {
                   
                  #  Input check
                  input.corr = T
                  
                  if (input$perday != 288 && input$perday != 96) {
                    input.corr = F
                    output$input_check = renderText("Invalid number of time points per day. Accepted 288 or 96.")
                  }
                  if(class(input$dtformat) != "character") {
                    input.corr = F
                    output$input_check = renderText("Invalid Date format.")
                  }
                  if(class(input$idcol) != "integer") {
                    input.corr = F
                    output$input_check = renderText("Invalid Id column number.")
                  }
                  if(class(input$idrow) != "integer") {
                    input.corr = F
                    output$input_check = renderText("Invalid Id row number.")
                  }
                  if(class(input$headnrows) != "integer") {
                    input.corr = F
                    output$input_check = renderText("Invalid number of header rows.")
                  }
                  if(class(input$datecol) != "integer") {
                    input.corr = F
                    output$input_check = renderText("Invalid column number of dates.")
                  }
                  if(class(input$timecol) != "integer") {
                    input.corr = F
                    output$input_check = renderText("Invalid column number of hours.")
                  }
                  if((class(input$dtcol) != "integer") && (is.na(input$dtcol) == FALSE)) {
                    input.corr = F
                    output$input_check = renderText("Invalid column number of date and hour.")
                  }
                  if(class(input$glucosecol) != "integer") {
                    input.corr = F
                    output$input_check = renderText("Invalid column number of glucose values.")
                  }
                  
                  if(input$separator == "tab") {
                    print("hello")                  
                    sep.value = "\t"
                  }
                  # Here is where the magic happens - listofmeasurements declaration
                  if (input.corr ==T )
                    {
                    d = tryCatch(
                      {
                        ListOfMeasurments$new(files.list = unlist(input$files$datapath),
                                        dir = getwd(), max.days = T, perday = input$perday,
                                        idrow = input$idrow, 
                                        idcol = input$idcol,
                                        headnrows = input$headnrows, 
                                        datecol = input$datecol,
                                        timecol = input$timecol, 
                                        dtcol = input$dtcol,
                                        glucosecol = input$glucosecol,
                                        separator = input$separator,
                                        extension = input$extension, 
                                        dtformat = input$dtformat
                                        )
                      },
                      error = function(cond) {
                        output$text.error.d = renderText(paste0("Errors during creating ListOfMeasurement. Check whether input fields are correctly specified. Original
                                                                error message: \n", cond))
                        return(NA)
                      },
                      finally = {
                        
                      }
                    )
                  
                  # getResults invokes calculate class to calculate all indices and returns dataframe of results
                  setProgress(value = 0.5, message = "Done loading and preprocessing", detail = "Now calculating. (up to a couple of minutes)")
                  res = NA
                  if(!is.na(d)) {
                    res = tryCatch(
                      {
                        d$getResults()
                      },
                      error = function(cond) {
                        output$text.error.getRes = renderText(paste0("Errors during calculating results. Please contact the autor. Original
                                                                error message: \n", cond))
                        return(NA)
                      },
                      finally = {
                        
                      }
                    )
                  }
                  output$table = renderTable(res)
                  
                  setProgress(value = 1, message = "Done calculating", detail = "Your download will soon be ready. Go to 'Output' tab.")
                  Sys.sleep(4)
                  
                  # downloadHandler to handle creating csv files to output. I tried it with write.xlsx, but it didn't work, so I left it as a csv.
                  if(!is.na(res))
                  {output$downloadResults = downloadHandler(
                    filename = function() {
                      paste ("Results generated at ", Sys.time(), ".csv", sep = "")
                    },
                    content = function(file) {
                      write.csv(res, file, sep = '\t', eol = '\r\n', dec = '.')
                    }
                  )}
                  }
    })
  })
})
