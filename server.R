library (shiny)

shinyServer(function(input, output, session) {
  output$directory = renderText(input$fileIn$datapath)
})