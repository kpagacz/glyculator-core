if (!require("shinythemes")) { install.packages("shinythemes")}
library (shiny)
library (shinythemes)
library(shinyBS)



Introduction = tabPanel(title = "Introduction")

shinyUI (
    fluidPage(theme = shinytheme("yeti"),
              tags$head(
                tags$link(rel = "stylesheet", type = "text/css", href = "konsta.css"),
                
                HTML("<link rel=\"author\" href=\"https://plus.google.com/109644123848417917359\" />"),
                HTML("<script>
         (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
         (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
         m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
         })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
         
         ga('create', 'UA-53584749-4', 'auto');
         ga('send', 'pageview');
         
         </script>")
              ),
      titlePanel("GlyCulator 2.0"),
      p(
      tabsetPanel(
      tabPanel("Input",
                 fluidRow(
                   column(6, offset = 0, 
                    numericInput ("idrow", label = "Identificator's row number", value = 3),
                    numericInput ("idcol", label = "Identificator's column number", value = 2),
                    numericInput ("perday", label = "Number of time points per day", value = 288),
                    numericInput ("headnrows", label = "Number of header rows", value = 13),
                    numericInput ("datecol", label = "Column number of dates", value = 2),
                    numericInput ("timecol", label = "Column number of hours", value = 3),
                    numericInput ("dtcol", label = "Column number of date and hour", value = 4),
                    numericInput ("glucosecol", label = "Column number of glucose values", value = 10)
                    ),
                   column (6,
                     textInput ("dtformat", label = "Date format", value = "dmy_hms"),
                     #textInput ("maxdays", label = "Calculate from maximum number of whole days?", value = "F"),
                     bsTooltip("dtformat", "Please specify the order of day, month, year as well as hours, minutes and optionally seconds. E.g.: mdy_hm for a format like this: 9/27/99 13:13; ymd_hms for a format like this: 17.10.21 13:41:59. The seperator can be: :, ., /",
                               "right", options = list(container = "body")),
                     #textInput ("extension", label = "File extension", value = ".csv"),
                     selectInput("extension", "File extension",
                                 c("Comma-seperated (.csv)" = ".csv",
                                   "Text file (.txt)" = ".txt",
                                   "Microsoft Excel (.xlsx)" = ".xlsx",
                                   "Microsoft Excel before 2003 (.xls)" = ".xls")),
                     textInput ("separator", label = "Separator", value = ","),
                     fileInput ('files', label = 'Upload files:', multiple = T),
                     actionButton("button", "Confirm parameters and file input"),
                     textOutput("input_check")
                   )
                 )
      ),
      tabPanel(title = "Output",
                 fluidRow(
                   textOutput('complete')
                   ),
               fluidRow(
                 textOutput("text.error.d")
               ),
               fluidRow(
                 textOutput("text.error.getRes")
               ),
                 fluidRow(
                   downloadButton('downloadResults', "Download Results!")
                   ),
                 fluidRow(
                   tableOutput("table")
                 )
      ),
      tabPanel(title = "Instructions - how to use",
                 fluidRow(
                   tags$div(
                     list(
                        tags$p ("The most important while using GlyCulator2 is: the program requires files analyzed to be formatted in a uniform way. Since a user is asked to provide some information about the files, the pieces of information need to hold true for all files provided. If a user wants to analyze two types of files, I recommend to prepare two batches of files and analyze them with GlyCulator2 seperately."),
                       tags$p ("Glyculator2 requires user to submit: (please note that the numbering of columns and rows begins from 1)",
                               tags$ul(
                                 tags$li("column number and row number of a cell which contains a name or identification of each file (must be the same in all files)"),
                                 tags$li("number of time points per day - which is related to the interval of the recordings. Please input 288, if the interval is 5 minutes"),
                                 tags$li("number of header rows in all files - this an optional argument. If your files do not contain headers, change it to 0"),
                                 tags$li("you have to specify either the numbers of columns with dates and hours or the number of a column which contains the full date. If your files contain no column with date and hour, please leave the field blank. If your files do not have two seperate columns with dates and numbers, you can leave the appropriate fields empty or leave them as they are. GlyCulator2 will take only the column with date and hour to consideration"),
                                 tags$li("column number with glucose values"),
                                 tags$li("format of the date: please specify the order of day, month, year as well as hours, minutes and optionally seconds. E.g.: mdy_hm for a format like this: 9/27/99 13:13; ymd_hms for a format like this: 17.10.21 13:41:59. The seperator can be: :, ., /"),
                                 tags$li("provide file extension of your files. Currently supported are: .csv, .txt, .xlsx, .xls"),
                                 tags$li("if your files are in a .csv format, please provide a character which fulfills the seperator role in your files"),
                                 tags$li("files to analyze. You can choose any files from you PC, by clicking the <Browse> button.")
                               )),
                       tags$p("To better illustrate what is what in a CGM file, following images of a raw CGM data file are marked with names of input fields."),
                       tags$div(img(src = "arg cols.jpg", width = 770, height = 306, align = "center", title = "Column numbers explained", Introduction = "Column numbers explained")),
                       tags$div(img(src = "header.jpg", width = 959, height = 201, Introduction = "Header rows number")),
                       tags$div(img(src = "id expl.jpg", width = 563, height = 214, Introduction = "ID cell row and column number")),
                       tags$p("Further instructions and explanations can be found in a manual document.",
                              tags$a(href="https://zbimt-cloud.konsta.com.pl/s/h45u414p1yqyfsS", "Click here to download manual.")
                              )
                      
                       
                     )
                   )
                    
                 )
      ),
      tabPanel(title = "About",
                 fluidRow(
                    tags$div(
                      list (
                        tags$p ("GlyCulator2 was created by Konrad Pagacz to calculate glycaemic variability indices from raw continuous glucose monitoring 
                        (CGM) or flash glucose monitoring (FGM) data. It accepts raw CGM or FGM files in .xls, .xlsx, .csv, .txt formats and calculates
                        the following glycaemic variability indices:"),
                        tags$ul (
                          tags$li("mean"),
                          tags$li("standard deviation (SD)"),
                          tags$li("median, coefficient of variation (CV), M100 index"),
                          tags$li("low/high blood glucose index"),
                          tags$li("estimated HbA1c"),
                          tags$li("J-index"),
                          tags$li("mean amplitude of glycaemic excursion (MAGE)"),
                          tags$li("mean of daily differences (MODD)"),
                          tags$li("continuous overall net glycaemic action (CONGA)"),
                          tags$li("percent of measurements below 70 mg/dl (3.9 mmol)"),
                          tags$li("percent of measurements over 180 mg/dl (10 mmol/l)"), 
                          tags$li("glycaemic risk assessment in diabetes equation (GRADE) and GRADE's appropriate percentages.")
                        )
                      )
                    ),
                    tags$div (
                      tags$p ("The tool follows guidelines on CGM reporting specified in the International Consensus on Use
                              of Continuous Glucose Monitoring.")
                    ),
                    tags$div (
                      tags$p ("M100, J-index were calculated using formulas provided by F. John Service in:
                              Service, F. J. (2013). Glucose Variability. Diabetes, 62(5), 1398–1404. http://doi.org/10.2337/db12-1396."),
                      tags$p ("MAGE algorithm was adapted from: Baghurst, P. A. (2011). Calculating the mean amplitude of 
                              glycemic excursion from continuous glucose monitoring data: an automated algorithm. Diabetes 
                              Technology & Therapeutics, 13(3), 296–302. https://doi.org/10.1089/dia.2010.0090."),
                      tags$p ("MODD and CONGA algorithms were implemented after: McDonnell, C. M., Donath, S. M., Vidmar, 
                              S. I., Werther, G. a, & Cameron, F. J. (2005). A novel approach to continuous glucose 
                              analysis utilizing glycemic variation. Diabetes Technology & Therapeutics, 7(2), 253–63.
                              https://doi.org/10.1089/dia.2005.7.253."),
                      tags$p ("GRADE calculations follow: Hill, N. R., Hindmarsh, P. C., Stevens, R. J., 
                              Stratton, I. M., Levy, J. C., & Matthews, D. R. (2007). A method for assessing quality 
                              of control from glucose profiles. Diabetic Medicine : A Journal of the British
                              Diabetic Association, 24(7), 753–8. https://doi.org/10.1111/j.1464-5491.2007.02119.x.")
                    ),
                    tags$div(
                      tags$p("Further instructions and explanations can be found in a manual document.",
                             tags$a(href="https://zbimt-cloud.konsta.com.pl/s/h45u414p1yqyfsS", "Click here to download manual.")
                      ),
                      tags$a(href="https://zbimt-cloud.konsta.com.pl/s/bJY6pVUkD7IoX4s", "Click here to download the old version of GlyCulator - GlyCulator1.")
                    )
                )
    )
    )),
    hr(),
    p(HTML("<a href=\"#\">This software is a part of paper entitled 'GlyCulator2: an update on a web application for calculation of glycemic variability indices' and authored by Konrad Pagacz, Konrad Stawiski, Agnieszka Szadkowska, Wojciech Mlynarski, Wojciech Fendler.</a>"),
      br(),
    HTML("<a href=\"https://zbimt-cloud.konsta.com.pl/s/bJY6pVUkD7IoX4s\"> Click here to download old version of GlyCulator - GlyCulator 1.0.</a>"),
        HTML(paste0("<table border='0' width='100%'><tr><td><i>© Version 2.0 revision ", system("git rev-list HEAD --count", intern = TRUE) ," (", system("git log -1 --pretty='%H'", intern = TRUE) ,")</i><br /><a href='http://biostat.umed.pl'><font size='1'>Software author, technical issues: <br/><b>Konrad Pagacz, MD</b> (contact: konrad.pagacz@umed.lodz.pl; Department of Biostatistics and Translational Medicine, Medical University of Lodz, Poland)</font></a></td><td><img align='right' width='200' src='logo.png'/></td></tr></table>"))
  ))
)