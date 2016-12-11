library(shiny)
library(ggplot2)
library(DT)

shinyServer(function(input, output, session) {
  df <- reactive({
    inFiles <- input$fileIn
    df <- data.frame()
    if (is.null(inFiles))
      return(NULL)
    for (i in seq_along(inFiles$datapath)) {
      tmp <- read.csv(inFiles$datapath[i], header = FALSE)  
      df <- rbind(df, tmp)
    }
    df
    
  })
  output$tbl <- DT::renderDataTable(
    df()
  )
  output$tbl2 <- DT::renderDataTable(
    input$fileIn
  )
  output$results = renderPrint({
    input$mydata
  })
  
})