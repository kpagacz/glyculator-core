library ('R6')
library ('xlsxjars') 
library ('xlsx')
library ('dplyr')
library ('ttutils')
library ('lubridate')
library ('stringr')
library ('ggplot2')
library ('fractal')
#source ('theme_default.R')


###########################
Measurement = R6Class ('Measurement',
                       public = list (
                         file = NA,
                         perday = NA,
                         id = NA,
                         interval = NA,
                         dtformat = '',
                         max.days = F,
                         
                         initialize = function (file, perday = 288, dtformat, max.days) {
                           
                           private$getID(file)
                           self$dtformat = dtformat
                           self$file = suppressWarnings(private$prepareDf(file, dtformat = self$dtformat))
                           self$perday = perday
                           self$interval = 1440/perday
                           self$max.days = max.days
                           validation = private$validate()
                           if (validation==FALSE) cat('Your input is incorrect. Check whether the number of measurements per day is correct. Only 288 or 96 are being accepted.\n')
                           self$makePretty()
                           if (max.days == F) {
                             self$file = self$file[private$getIndOf10PM():(private$getIndOf10PM()-1+self$perday*2),]
                           }
                         },
                         
                         makePretty = function () {
                           private$cutNAs()
                           #suppressWarnings(private$cutNAsFromBeg())
                           #suppressWarnings(private$cutNAsFromEnd())
                           suppressWarnings(private$cutDup())
                           suppressWarnings(private$cutTTTTTT())
                           suppressWarnings(private$cutTTTT())
                           suppressWarnings(private$cutTT())
                           
                           if (suppressWarnings(self$areBreaks()) == TRUE) suppressWarnings(private$cutBreaks())
                           if (self$areNAs() == TRUE) cat ('NAs w wynikach glikemii w pliku', self$id, '.xls. Opracuj plik recznie.\n')
                           private$appendIndex()
                           rownames(self$file) = NULL
                         },
                         
                         areDiff5 = function() {
                           datelagged = c(.POSIXct(double(length(self$file$DT))))
                           datelagged[-1] = self$file$DT
                           datediff = abs(difftime(datelagged, self$file$DT, units = 'secs'))
                           logical = datediff > self$interval*60 - 2 & datediff < self$interval*60 + 2
                           logical[1] = TRUE
                           #cat(datediff, logical)
                           return(all(logical))
                         },
                         
                         areBreaks = function() {
                           datediff = abs(difftime(self$file$DT[-1], head(self$file$DT, -1), units = 'secs'))
                           logical = datediff < self$interval*60 + 30
                           #cat (logical, "\n")
                           #print (!all(logical))
                           return(!all(logical))
                         },
                         
                         areNAs = function() {
                           if(all(!is.na(self$file$Glucose))) return(FALSE) else return(TRUE)
                         },
                         
                         writeXLS = function(dir = getwd()) {
                           #Date = as.data.frame(paste(day(self$file$DT), month(self$file$DT), substr(year(self$file$DT),3,4), sep = '.'))
                           Dates = self$file$DT
                           years = year(Dates)
                           months = month(Dates)
                           days = day(Dates)
                           
                           #years = str_pad(years, width = 2, side = 'left', pad = '0')
                           years = substr(years,3,4)
                           months = str_pad(months, width = 2, side = 'left', pad = '0')
                           days = str_pad (days, width = 2, side = 'left', pad = '0')
                           
                           DatesColumn = paste(days, months, years, sep = '.')
                           
                           #Time = as.data.frame(paste(hour(self$file$DT), minute(self$file$DT), second(self$file$DT), sep = ':'))
                           Time = self$file$DT
                           hours = hour(Time)
                           minutes = minute(Time)
                           seconds = second (Time)
                           
                           hours = str_pad(hours, width = 2, side = 'left', pad = '0')
                           minutes = str_pad(minutes, width = 2, side = 'left', pad = '0')
                           seconds = str_pad(seconds, width = 2, side = 'left', pad = '0')
                           TimeColumn = paste(hours,minutes,seconds, sep = ':')
                           
                           output = data.frame(DatesColumn, TimeColumn, self$file$Glucose)
                           colnames(output) = c('Date', 'Time', 'Sensor')
                           FileName = gsub(" ", "", self$id)
                           FileName = gsub("\\?", "_", FileName)
                           write.xlsx (output, file = paste(dir, '/', FileName, '.xls', sep =''), showNA=FALSE, row.names=FALSE)
                         }
                        ),
                        private = list (
                         
                         validate = function () {
                           if (self$perday!=96 & self$perday!=288) {return (FALSE)} else {return(TRUE)}
                         },
                         
                         prepareDf = function(df, dtformat) {
                           df = data.frame(df$Glucose, df$DT)
                           dfGlucose = df[[1]]
                           intgluc = as.numeric(levels(dfGlucose))[dfGlucose]
                           df$Glucose = intgluc
                           df$df.DT = do.call(dtformat, list(df$df.DT))
                           df = data.frame(df$df.DT, df$Glucose)
                           colnames(df) = c('DT', 'Glucose')
                           return (df)
                         },
                         
                         getID = function (df) {
                           self$id = df[1,3]
                         },
                         
                         appendIndex = function() {
                           ids = data.frame(1:nrow(self$file))
                           #cat (ids)
                           self$file = data.frame (self$file$DT, self$file$Glucose, ids[1])
                           colnames(self$file) = c('DT', 'Glucose', 'ID')
                         },
                         
                         cutDup = function () {
                           # cut duplicates and differing by 1 sec (for some reason the second part of cutShorter5andDup left them intact)
                           datelagged = self$file$DT
                           datelagged[-1] = self$file$DT
                           #print(datelagged)
                           datediff = abs(difftime(datelagged, self$file$DT, units = 'secs'))
                           datediff = datediff[-length(datediff)]
                           dup = datediff == 0 | datediff == 1
                           dupint = seq.int(length=length(dup))
                           dupint = dupint[dup]
                           if(length(dupint) > 0) self$file = self$file[-dupint,]
                         },
                         
                         cutTTTTTT = function () {
                           datelagged2 = c(.POSIXct(double(length(self$file$DT))))
                           datelagged2[-1] = self$file$DT
                           datediff2 = abs(difftime(datelagged2, self$file$DT, units = 'secs'))
                           datediff2 = datediff2[-length(datediff2)]
                           logical2 = datediff2 < self$interval * 60 - 2 - (self$perday==96) * 60
                           logical2[1] = FALSE
                           patrn2 = as.logical(c('TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE', 'TRUE'))
                           m2 = length(patrn2)
                           n2 = length(logical2)
                           candidate2 = seq.int(length = n2-m2+1)
                           for (i in seq.int(length=m2)) {
                             candidate2 = candidate2[patrn2[i] == logical2[candidate2 + i -1]]
                           }
                           if (length(candidate2) > 0) self$file = self$file[-candidate2,]
                         },
                           
                         cutTTTT = function() {
                         # cut second value of a seq of DTs like this one: 1:00 1:30 6:00 6:30 11:00, which was very annoying to deal with otherwise
                           datelagged2 = c(.POSIXct(double(length(self$file$DT))))
                           datelagged2[-1] = self$file$DT
                           datediff2 = abs(difftime(datelagged2, self$file$DT, units = 'secs'))
                           datediff2 = datediff2[-length(datediff2)]
                           logical2 = datediff2 < self$interval * 60 - 2- (self$perday==96) * 60
                           logical2[1] = FALSE
                           patrn2 = as.logical(c('TRUE', 'TRUE', 'TRUE', 'TRUE'))
                           m2 = length(patrn2)
                           n2 = length(logical2)
                           candidate2 = seq.int(length = n2-m2+1)
                           for (i in seq.int(length=m2)) {
                              candidate2 = candidate2[patrn2[i] == logical2[candidate2 + i -1]]
                           }
                           if (length(candidate2) > 0) self$file = self$file[-candidate2,]
                         },
                         
                         cutTT = function () {
                           # cut, cut :P
                           datelagged3 = c(.POSIXct(double(length(self$file$DT))))
                           datelagged3[-1] = self$file$DT
                           datediff3 = abs(difftime(datelagged3, self$file$DT, units = 'secs'))
                           datediff3 = datediff3[-length(datediff3)]
                           logical3 = datediff3 < self$interval * 60 - 2 - (self$perday==96) * 60
                           logical3[1] = FALSE
                           patrn3 = as.logical (c('TRUE', 'TRUE'))
                           m3 = length(patrn3)
                           n3 = length(logical3)
                           candidate3 = seq.int(length = n3-m3+1)
                           for (i in seq.int(length=m3)) {
                              candidate3 = candidate3[patrn3[i] == logical3[candidate3 + i -1]]
                           }
                           if (length(candidate3) > 0) self$file = self$file[-candidate3,]
                          },
                         
                         cutBreaks = function() {
                           datediff = abs(difftime(self$file$DT[-1], head (self$file$DT, -1), units = 'mins'))
                           StartIndex = 1
                           EndIndex = 1
                           StartIndexLongest = 0
                           EndIndexLongest = 0
                           Longest = 0
                           for (i in 1:length(datediff)) {
                             if (datediff[i] < self$interval + 0.08 * self$interval) {
                               EndIndex = i
                             } else {
                               if (EndIndex - StartIndex > Longest) {
                                 StartIndexLongest = StartIndex
                                 EndIndexLongest = EndIndex
                                 Longest = EndIndex - StartIndex
                               }
                               StartIndex = i + 1
                               EndIndex = i + 1
                             }
                           }
                           
                           if (EndIndex - StartIndex > Longest) {
                             StartIndexLongest = StartIndex
                             EndIndexLongest = EndIndex
                             Longest = EndIndex - StartIndex
                           }
                           
                           if (Longest < self$perday * 2) {
                             cat ("There is no continous 48 hours-long part of", self$id, "file. The measurement will be excluded from further analysis. \n", sep = " ")
                           } else {
                             self$file = self$file[StartIndexLongest:EndIndexLongest+1,]
                           }
                          },
                         
                         cutNAs = function(){
                           self$file = self$file[!is.na(self$file$Glucose),]
                          },
                         
                         getIndOf10PM = function () {
                           logic = hour(self$file[,1])==22
                           first = min(which(logic==T))
                           return (first)
                         }
                           
                           ),
                       active = list(
                         
                       )
)

# As an input: a single data.frame with at least 5 columns: Date, Time, DateTime,  Glucose, ID.

##########################
ListOfMeasurments = R6Class ('ListOfMeasurments',
                             
                             public = list (
                               
                              idrow = 0,
                              idcol = 0,
                              headnrows = 0,
                              dtcol = 0,
                              glucosecol = 0,
                              perday = 0,
                              datecol = 0,
                              timecol = 0,
                              separator = '',
                              extension = '',
                              dtformat = '',
                              max.days = F,
                              
                              
                              initialize = function (list = NA, dir = getwd(), max.days = F, perday = 288, idrow = 3, idcol = 2, headnrows = 13, datecol = 2, timecol = 3, dtcol = 4, glucosecol = 10, separator = ',', extension = '.csv', dtformat = 'dmy_hms') {
                                #self$removeMeasurementsWithNAs()
                                
                                self$idrow = idrow
                                self$idcol = idcol
                                self$headnrows = headnrowslo 
                                self$dtcol = dtcol
                                self$glucosecol = glucosecol
                                self$perday = perday
                                self$extension = extension
                                self$separator = separator
                                self$dtformat = dtformat
                                self$max.days = max.days
                                
                                if(!is.na(list)) private$aftertrim = list else self$loadFromDir(dir, perday = self$perday, dtformat = self$dtformat, max.days = self$max.days)
                                #print(private$lob2)
                                self$removeMeasurementsWithBreaks()
                                #print(self$get_lob())
                                
                              },
                              
                              loadFromDir = function (dir = getwd(), perday, dtformat, max.days) {
                                private$beforetrim = private$readCSVs (dir = dir)
                                cat ('Done loading.\n')
                                private$aftertrim = private$trimAll ()
                                cat('Done trimming.\n')
                                
                                listofobjects = lapply (private$aftertrim, function (x) {
                                  NewMeasure = Measurement$new(x,perday,dtformat = dtformat,max.days = max.days)
                                  #NewMeasure$makePretty() print (NewMeasure)
                                  return (NewMeasure)
                                } 
                                )
                                
                                private$lob2 = listofobjects
                                
                              },
                              
                              get_aftertrim = function () {
                                return(private$aftertrim)
                              },
                              
                              get_lob = function() {
                                return (private$lob2)
                              },
                              
                              get_loids = function () {
                                vector = sapply (self$get_lob(), function (x) { 
                                    return (x$id)
                                  }
                                  )
                                return (vector)
                              },
                              
                              writeDfs = function (dir = getwd()) {
                                
                                for (df in private$aftertrim) {
                                  name = as.character(df[1,4]) 
                                  filedir = paste(dir, '/dane/', name, '.xls', sep = '')
                                  write.xlsx(df, filedir, row.names=FALSE, showNA=FALSE)
                                  
                                }
                              },
                              
                              writeMeasurements = function (dir = getwd()) {
                                for (measure in private$lob2) {
                                  measure$writeXLS(dir)
                                }
                              },
                              
                              getResults = function () {
                                #Results = Calculate1$new(private$lob2[[1]])$getOutput()
                                Results = structure(list(), class = "data.frame")
                                for (i in seq.int(length.out = length(self$get_lob()))) {
                                  res = Calculate1$new(self$get_lob()[[i]])$getOutput()
                                  #print (res)
                                  Results = rbind (Results, res)
                                  #cat(i, ' input \n')
                                }
                                
                                write.xlsx (Results, 'Results.xlsx', showNA = F)
                                print(c("Results saved to Results.xlsx"))
                                return (Results)
                              
                              },
                              
                              removeMeasurementsWithNAs = function () {
                                print("haha")
                                NAsLogicVector = sapply (self$get_lob(), function(x) {
                                  return (x$areNAs())  
                                }
                                )
                                #print (NAsLogicVector)
                                private$lob2 = private$lob2[!NAsLogicVector]
                              },
                              
                              removeMeasurementsWithBreaks = function() {
                                BreaksLogicVector = vector()
                                BreaksLogicVector = sapply (self$get_lob(), function (x) {
                                  return (x$areBreaks())
                                }
                                )
                                #print (BreaksLogicVector)
                                private$lob2 = private$lob2[!BreaksLogicVector]
                              },
                              
                              printIDs = function () {
                                arr = sapply (self$get_lob(), function(x) {
                                  return (x$id)
                                  }
                                  )
                                arr
                              },
                              
                              getPlots = function() {
                                lop = lapply (self$get_lob(), function (x) {
                                    plot = ggplot(x$file, aes (x = DT, y = Glucose)) + 
                                      geom_point() + 
                                      theme_default +
                                      #scale_x_continuous(name = "Time Stamp") +
                                      expand_limits(y=0) +
                                      scale_y_continuous(expand = c(0,0), limits = c(0,1.05*max(x$file[2])))
                                    return (plot)
                                }
                                )
                                return(lop)
                              },
                              
                              printPlots = function() {
                                pdf("glycemiaplots.pdf")
                                for (plot in self$getPlots()) {
                                  print (plot)
                                }
                                dev.off()
                              }
                             
                             ),
                             
                             private = list (
                               lob2 = list(),
                               beforetrim = NA,
                               aftertrim = NA,
                               
                               readCSVs = function (dir = getwd(), ext = self$extension, separator = self$separator) {
                                 
                                 FileNames = list.files (dir, pattern = paste('*', ext, sep = ''), full.names = TRUE)
                                 ListOfDfs = lapply (FileNames, read.csv, sep = separator, header = FALSE, encoding = "UTF-16")
                                 return (ListOfDfs)
                               },
                               
                               trimDf = function (df, dtcol = self$dtcol, datecol = self$datecol, timecol = self$timecol, glucosecol = self$glucosecol) {
                                 id = as.character(df[self$idrow[[1]], self$idcol[[1]]])
                                 #cat(id)
                                 #print(NewDf)
                                 if(is.na(dtcol)) {
                                   dtcol = ncol(df)+1
                                   df = private$joinDateAndTime(df, datecol = datecol, timecol = timecol, dtcol = dtcol)
                                 }
                                 NewDf = df[self$headnrows:nrow(df),]
                                 NewDf = NewDf[,c(dtcol,glucosecol)]
                                 norows = nrow(NewDf)-10
                                 NewDf = NewDf[1:norows,]
                                 rownames (NewDf) = NULL
                                 #print(NewDf)
                                 NewDf[1,3] = id
                                 colnames(NewDf) = c('DT', 'Glucose')
                                                       #, 'ID')
                                 #print (NewDf)
                                 return (NewDf)
                                 },
                               
                               joinDateAndTime = function (df, datecol, timecol, dtcol) {
                                 df[,dtcol] = paste (df[,datecol], df[,timecol])
                                 return (df)
                               },
                               
                               trimAll = function (file = private$beforetrim) {
                                 aftertrim = lapply (file, private$trimDf)
                                 return (aftertrim)
                               }
                               
                               
                               
                             )
)

###############################
Calculate1 = R6Class ('Calculate1',
                      public = list (
    
    
                        initialize = function (Meas) {
                          private$Measurement = Meas
                          rownames(private$Output) = Meas$id
                          colnames(private$Output) = 'Number of measurements'
                          self$calculateEverything()
                        },
    
                        getMeasurement = function () {
                        return (private$Measurement)
                        },
    
                        getOutput = function() {
                          return (as.data.frame(private$Output))
                        },
    
                        calculateEverything = function () {
                          private$calculateNoDaysAndNoRecords()
                          if (private$NoDays >= 2) {
                          private$calculateMean()
                          private$calculateSD()
                          private$calculateMedian()
                          private$calculateCV()
                          private$calculateM100()
                          private$calculateJ()
                          private$calculateMAGE()
                          private$calculateMODD()
                          private$calculateCONGA1h()
                          private$calculateCONGA2h()
                          private$calculateCONGA3h()
                          private$calculateCONGA4h()
                          private$calculateCONGA6h()
                          private$calculateHypo()
                          private$calculateHyper()
                          private$calculateSlope1()
                          private$calculateSlope2()
                          private$calculateSlope3()
                          } else {
                          cat ("Insufficient number of measurement time points (needed at least 496) to calculate parameters in file", private$Measurement$id,".\n", sep = ' ')
                            private$Output$Mean = NA
                            private$Output$SD = NA
                            private$Output$Median = NA
                            private$Output$CV = NA
                            private$Output$M100 = NA
                            private$Output$J = NA
                            private$Output$MAGE = NA
                            private$Output$MODD = NA
                            private$Output$CONGA1h = NA
                            private$Output$CONGA2h = NA
                            private$Output$CONGA3h = NA
                            private$Output$CONGA4h = NA
                            private$Output$CONGA6h = NA
                            private$Output$Percent_of_measurements_below_70mgdl = NA
                            private$Output$Percent_of_measurements_over_180mgdl = NA
                            private$Output$Alpha1_DFA = NA
                            private$Output$Alpha2_DFA = NA
                            private$Output$Alpha3_DFA = NA
                        }
                      }
                      ),
                      private = list (
                        Measurement = NULL,
                        Output = data.frame (matrix(nrow = 1)),
                        NoDays = NULL,
                        NoRecords = NULL,
    
    
                        calculateNoDaysAndNoRecords = function () {
                          NoDays = floor(nrow(private$Measurement$file)/private$Measurement$perday)
                          private$NoDays = NoDays
                          #IMPORTANT: next line is setting the days to calculate
                          private$NoRecords = NoDays*private$Measurement$perday
                          private$Output[1,1] = nrow (private$Measurement$file)
                        },
    
                        calculateMean = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Mean = mean(df$Glucose, na.rm = TRUE)
                          private$Output$Mean = Mean
                        },
    
                        calculateSD = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          SD = sd(df$Glucose, na.rm = TRUE)
                          private$Output$SD = SD
                        },
    
                        calculateMedian = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Median = median(df$Glucose, na.rm = TRUE)
                          private$Output$Median = Median
                        },
    
                        calculateCV = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          CV = 100 * (sd(df$Glucose, na.rm = TRUE)/mean(df$Glucose, na.rm = TRUE))
                          private$Output$CV = CV
                        },
    
                        calculateM100 = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          M100 = mean(1000*abs(log(df$Glucose/100, 10)))
                          private$Output$M100 = M100
                        },
                        
                        calculateJ = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Mean = mean(df$Glucose, na.rm = TRUE)
                          SD = sd(df$Glucose, na.rm  = TRUE)
                          J = 0.001 * (Mean + SD)
                          private$Output$J = J
                        },
                        
                        calculateMAGE = function() {
                          v = private$Measurement$file$Glucose[1:private$NoRecords]
                          #print (c(private$Measurement$id, " \n"))
                          #v = as.vector(df$Glucose)
                          #printing vector
                          #cat (v, '\n', length(v), "\n")
                          if (v[1] < v[2]){
                            up = 0
                          } else if (v[1] > v[2]){
                            up = 1
                          } else if (v[1] == v[2]) {
                            up = 2
                          }
                          PeaksNadirs = vector()
                          for (i in seq.int(length.out = (length(v)-1))) {
                            if (v[i] - v[i+1] > 0) {
                              if (up == 1) PeaksNadirs = append(PeaksNadirs, v[i])
                              up = 0
                            } else if (v[i] - v[i+1] < 0) {
                              if (up == 0) PeaksNadirs = append(PeaksNadirs, v[i])
                              up = 1
                            }
                          }
                          PeaksNadirs = append(PeaksNadirs, v[length(v)])
                          #printingPeaksNadirs
                          #cat(PeaksNadirs)
                          PeaksNadirsDiff = vector()
                          for (j in seq.int(length.out = (length(PeaksNadirs)-1))){
                            #important line here - defining what excursion is
                            if (abs(PeaksNadirs[j] - PeaksNadirs[j+1]) - 2*private$Output$SD > 0){
                              PeaksNadirsDiff = append(PeaksNadirsDiff, abs(PeaksNadirs[j]-PeaksNadirs[j+1]))
                            }
                          }
                          #printing PNDiff
                          #cat(PeaksNadirsDiff)
                          MAGE = mean(PeaksNadirsDiff)
                          private$Output$MAGE = MAGE
                        },
                        
                        calculateMODD = function() {
                            DayIntervalDiff = vector()
                            v = private$Measurement$file$Glucose[1:private$NoRecords]
                            for (i in seq.int (length.out = length(v)/2)){
                              DayIntervalDiff = append(DayIntervalDiff, abs(v[i] - v[i+private$Measurement$perday]))
                            }
                            #printing DayIntervalDiff
                            #cat(DayIntervalDiff)
                            MODD = mean (DayIntervalDiff)
                            private$Output$MODD = MODD
                        },
                        
                        calculateCONGA1h = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector(df$Glucose)
                          Hours = 1
                          Differences = vector()
                          for (i in seq.int(length.out = (length(Glucose) - (Hours*(private$Measurement$perday/24))))) {
                            Differences = append (Differences, abs(Glucose[i+(Hours*(private$Measurement$perday/24))]-Glucose[i]))
                          }
                          #cat(Differences)
                          Mean = mean(Differences)
                          CONGA = sqrt(sum((Mean - Differences)^2)/length(Differences) - 1)
                          #cat(CONGA)
                          private$Output$CONGA1h = CONGA
                        },
                        
                        calculateCONGA2h = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector(df$Glucose)
                          Hours = 2
                          Differences = vector()
                          for (i in seq.int(length.out = (length(Glucose) - (Hours*(private$Measurement$perday/24))))) {
                            Differences = append (Differences, abs(Glucose[i+(Hours*(private$Measurement$perday/24))]-Glucose[i]))
                          }
                          #cat(Differences)
                          Mean = mean(Differences)
                          CONGA = sqrt(sum((Mean - Differences)^2)/length(Differences) - 1)
                          #cat(CONGA)
                          private$Output$CONGA2h = CONGA
                        },
                        
                        calculateCONGA3h = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector(df$Glucose)
                          Hours = 3
                          Differences = vector()
                          for (i in seq.int(length.out = (length(Glucose) - (Hours*(private$Measurement$perday/24))))) {
                            Differences = append (Differences, abs(Glucose[i+(Hours*(private$Measurement$perday/24))]-Glucose[i]))
                          }
                          #cat(Differences)
                          Mean = mean(Differences)
                          CONGA = sqrt(sum((Mean - Differences)^2)/length(Differences) - 1)
                          #cat(CONGA)
                          private$Output$CONGA3h = CONGA
                        },
                        
                        calculateCONGA4h = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector(df$Glucose)
                          Hours = 4
                          Differences = vector()
                          for (i in seq.int(length.out = (length(Glucose) - (Hours*(private$Measurement$perday/24))))) {
                            Differences = append (Differences, abs(Glucose[i+(Hours*(private$Measurement$perday/24))]-Glucose[i]))
                          }
                          #cat(Differences)
                          Mean = mean(Differences)
                          CONGA = sqrt(sum((Mean - Differences)^2)/length(Differences) - 1)
                          #cat(CONGA)
                          private$Output$CONGA4h = CONGA
                        },
                        
                        calculateCONGA6h = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector(df$Glucose)
                          Hours = 6
                          Differences = vector()
                          for (i in seq.int(length.out = (length(Glucose) - (Hours*(private$Measurement$perday/24))))) {
                            Differences = append (Differences, abs(Glucose[i+(Hours*(private$Measurement$perday/24))]-Glucose[i]))
                          }
                          #cat(Differences)
                          Mean = mean(Differences)
                          CONGA = sqrt(sum((Mean - Differences)^2)/length(Differences) - 1)
                          #cat(CONGA)
                          private$Output$CONGA6h = CONGA
                        },
                        
                        calculateHypo = function () {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector(df$Glucose)
                          Percent = 100 * sum (Glucose < 70)/length (Glucose)
                          PrettyPercent = format (Percent, nsmall = 2, digits = 2, width = 4)
                          private$Output$Percent_of_measurements_below_70mgdl = Percent
                        },
                        
                        calculateHyper = function () {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector(df$Glucose)
                          Percent = 100 * sum (Glucose > 180)/length (Glucose)
                          PrettyPercent = format (Percent, nsmall = 2, digits = 2, width = 4)
                          private$Output$Percent_of_measurements_over_180mgdl = Percent
                        },
                        
                        calculateSlope1 = function () {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector(df$Glucose)
                          alpha1 = DFA(Glucose, scale.min = 2, scale.max = private$Measurement$perday/12)[[1]]
                          private$Output$Alpha1_DFA = alpha1
                        },
                        
                        calculateSlope2 = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector (df$Glucose)
                          alpha2 = DFA(Glucose, scale.min = private$Measurement$perday/12, scale.max = private$Measurement$perday/4)[[1]]
                          private$Output$Alpha2_DFA = alpha2
                        },
                        
                        calculateSlope3 = function() {
                          df = private$Measurement$file[1:private$NoRecords, ]
                          Glucose = as.vector (df$Glucose)
                          alpha3 = DFA(Glucose, scale.min = private$Measurement$perday/4, scale.max = private$Measurement$perday)[[1]]
                          private$Output$Alpha3_DFA = alpha3
                        }
),
                      active = list (
    
                      )
)

