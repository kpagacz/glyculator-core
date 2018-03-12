require (R6)
require (xlsx)
require (dplyr)
require (ttutils)
require (lubridate)
require (stringr)
require (ggplot2)
require(MESS)
require(data.table)

fillGaps = function (vector) {
  v = vector
  na = which(is.na(v))
  if (length(na)>0) {
    if (na[1] == 1) { na = na[-1] }
    for (i in na) {
      v[i] = (v[i-1] + v[i+1])/2
    }
  }
  return (vector)
}

getIndOfHour = function (vector, hour) {
  v = vector
  h = hour
  Ind = Position (f = function(x) {hour(x) == h}, x = v, right = F, nomatch = F)
  return (Ind)
}

night_block = c(0,24,1,2,3,4,5)
morning_block = c(6,7,8,9,10,11)
afternoon_block = c(12,13,14,15,16,17,18,19,20,21,22,23)

# lom = ListOfMeasurments$new(extension = '.txt', separator = '\t', max.days = T, glucosecol = 4, dtcol = 2, datecol = NA, timecol = NA, dtformat = 'ymd_hm', idcol = 1, idrow = 1, perday = 96)
# lom = ListOfMeasurments$new(extension = '.xlsx', glucosecol = 31, dtcol = NA, timecol = 3, datecol = 2, max.days = T, headnrows = 10, idrow = 1, idcol = 2, dtformat = 'ymd_hms')


###########################
Measurement = R6Class ('Measurement',
                       public = list (
                         file = NA,
                         filenas = NA,
                         perday = NA,
                         id = NA,
                         interval = NA,
                         dtformat = '',
                         max.days = F,
                         days = 2,
                         
                         initialize = function (file, perday = 288, dtformat, max.days) {
                           
                           #print("File in Measurement, beginning:")
                           #print(head(file))
                           private$getID(file)
                           self$dtformat = dtformat
                           #print(file)
                           self$file = (private$prepareDf(file, dtformat = self$dtformat))
                           #print(self$file)
                           self$perday = perday
                           self$interval = 1440/perday
                           self$max.days = max.days
                           validation = private$validate()
                           # if (validation==FALSE) cat('Your input is incorrect. Check whether the number of measurements per day is correct. Only 288 or 96 are being accepted.\n')
                           self$makePretty()
                         },
                         
                         makePretty = function () {
                           self$file$Glucose = private$fillGaps(self$file$Glucose)
                           suppressWarnings(private$cutDup())
                           suppressWarnings(private$cutTTTTTT())
                           suppressWarnings(private$cutTTTT())
                           suppressWarnings(private$cutTT())
                           self$filenas = self$file
                           private$cutNAs()
                           
                           #if (suppressWarnings(self$areBreaks()) == TRUE) suppressWarnings(private$cutBreaks())
                           #if (self$areNAs() == TRUE) #cat ('NAs w wynikach glikemii w pliku', self$id, '.xls. Opracuj plik recznie.\n')
                           #private$appendIndex()
                           rownames(self$file) = NULL
                           rownames(self$filenas) = NULL
                         },
                         
                         limitToMaxDays = function() {
                           # logic for max.days == F, it cuts down the number of records
                           Ind = private$getIndOfHour(vector = self$file$DT, hour = 22)
                           if ((Ind-1+self$perday*self$days)<=nrow(self$file)) {
                             self$file = self$file[Ind:(Ind-1+self$perday*self$days),]
                             return (T)
                           } else {
                             # cat("There is no continous 48 hours-long part of" , self$id, " file. The measurement will be excluded from further analysis.)\n")
                             return (F)
                           }
                         },
                         
                         areDiff5 = function() {
                           datelagged = c(.POSIXct(double(length(self$file$DT))))
                           datelagged[-1] = self$file$DT
                           datediff = abs(difftime(datelagged, self$file$DT, units = 'secs'))
                           logical = datediff > self$interval*60 - 2 & datediff < self$interval*60 + 2
                           logical[1] = TRUE
                           return(all(logical))
                         },
                         
                         areBreaks = function(perday = self$perday) {
                           datediff = abs(difftime(self$file$DT[-1], head(self$file$DT, -1), units = 'secs'))
                           logical = datediff < self$interval*60 + 30 + (perday == 96)*45
                           return(!all(logical))
                         },
                         
                         areNAs = function() {
                           if(all(!is.na(self$file$Glucose))) return(FALSE) else return(TRUE)
                         },
                         
                         writeXLS = function(dir = getwd()) {
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
                           df$Glucose = df[[1]]
                           if (class(df$Glucose) == "factor") {
                           intgluc = as.numeric(levels(df$Glucose))[df$Glucose]
                           df$Glucose = intgluc
                           }
                           df$df.DT = do.call(dtformat, list(df$df.DT))
                           df = data.frame(df$df.DT, df$Glucose)
                           colnames(df) = c('DT', 'Glucose')
                           #print(df)
                           return (df)
                         },
                         
                         getID = function (df) {
                           self$id = df[1,3]
                         },
                         
                         appendIndex = function() {
                           ids = data.frame(1:nrow(self$file))
                           self$file = data.frame (self$file$DT, self$file$Glucose, ids[1])
                           self$filenas = data.frame(self$filenas$DT, self$filenas$Glucose,ids[1])
                           colnames(self$file) = c('DT', 'Glucose', 'ID')
                           colnames(self$filenas) = c('DT', 'Glucose', 'ID')
                         },
                         
                         cutDup = function () {
                           # cut duplicates and differing by 1 sec (for some reason the second part of cutShorter5andDup left them intact)
                           datelagged = self$file$DT
                           datelagged[-1] = self$file$DT
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
                           StartIndexLongest = 1
                           EndIndexLongest = 1
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
                           if (Longest < self$perday*2) {
                             # cat ("There is no continous 48 hours-long part of", self$id, "file. The measurement will be excluded from further analysis. \n", sep = " ")
                           } else {
                             self$file = self$file[StartIndexLongest:(EndIndexLongest+1),]
                           }
                         },
                         
                         cutNAs = function(){
                           self$file = self$file[!is.na(self$file$Glucose),]
                         },
                         
                         getIndOfHour = getIndOfHour,
                         
                         fillGaps = fillGaps
                         
                       ),
                       active = list(
                         
                       )
)

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
                               files.list = NULL,
                               
                               
                               
                               initialize = function (files.list = NULL, dir = getwd(), max.days = T, perday = 288, idrow = 3, idcol = 2, headnrows = 13, datecol = 2, timecol = 3, dtcol = 4, glucosecol = 10, separator = ',', extension = '.csv', dtformat = 'dmy_hms') {
                                 #self$removeMeasurementsWithNAs()
                                 
                                 self$files.list = files.list
                                 self$idrow = idrow
                                 self$idcol = idcol
                                 self$headnrows = headnrows
                                 self$dtcol = dtcol
                                 self$glucosecol = glucosecol
                                 self$perday = perday
                                 self$extension = extension
                                 self$separator = separator
                                 self$dtformat = dtformat
                                 self$max.days = max.days
                                 self$datecol = datecol
                                 self$timecol = timecol
                                 
                                 if (is.null(self$files.list)) self$loadFromDir(dir, perday = self$perday, dtformat = self$dtformat, max.days = self$max.days) else 
                                   self$loadFromFiles (files.list = self$files.list, perday = self$perday, dtformat = self$dtformat, max.days = self$max.days)
                                 #self$removeShortMeasurements()
                                 #self$removeMeasurementsWithBreaks()
                                 if (self$max.days == F) self$limitMeasurementsToMaxDays()
                               },
                               
                               limitMeasurementsToMaxDays = function () {
                                 Logic = sapply (self$get_lob(), function (x) {
                                   return (x$limitToMaxDays())
                                 })
                                 Logic = unlist (Logic)
                                 private$lob2 = private$lob2[Logic]
                               },
                               
                               loadFromFiles = function (files.list = self$files.list, perday, dtformat, max.days) {
                                 private$beforetrim = private$readCSVs (FileNames = files.list)
                                 private$headers = private$readHeaders(FileNames = files.list)
                                 # cat ('Done loading.\n')
                                 private$aftertrim = private$trimAll ()
                                 # cat('Done trimming.\n')
                                 
          
                                 listofobjects = lapply (private$aftertrim, function (x) {
                                   
                                   NewMeasure = Measurement$new(x,perday,dtformat = dtformat,max.days = max.days)
                                   return (NewMeasure)
                                 } 
                                 )
                                 
                                 private$lob2 = listofobjects
                               },
                               
                               loadFromDir = function (dir = getwd(), perday, dtformat, max.days) {
                                 private$beforetrim = private$readCSVs (dir = dir)
                                 private$headers = private$readHeaders (dir = dir)
                                 # cat ('Done loading.\n')
                                 private$aftertrim = private$trimAll()
                                 # cat('Done trimming.\n')
                                 
                                 listofobjects = lapply (private$aftertrim, function (x) {
                                   #print("File sent to Meas")
                                   #print(head(x))
                                   NewMeasure = Measurement$new(x,perday,dtformat = dtformat,max.days = max.days)
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
                                 Results = structure(list(), class = "data.frame")
                                 for (i in seq.int(length.out = length(self$get_lob()))) {
                                   res = Calculate1$new(self$get_lob()[[i]])$getOutput()
                                   Results = rbind (Results, res)
                                 }
                                 # write.xlsx (Results, 'Results.xlsx', showNA = F)
                                 # print(c("Results saved to Results.xlsx"))
                                 Results = format(Results, nsmall = 2)
                                 return (Results)
                                 
                               },
                               
                               removeMeasurementsWithNAs = function () {
                                 NAsLogicVector = sapply (self$get_lob(), function(x) {
                                   return (x$areNAs())  
                                 }
                                 )
                                 private$lob2 = private$lob2[!NAsLogicVector]
                               },
                               
                               removeMeasurementsWithBreaks = function() {
                                 BreaksLogicVector = vector()
                                 BreaksLogicVector = sapply (self$get_lob(), function (x) {
                                   return (x$areBreaks())
                                 }
                                 )
                                 private$lob2 = private$lob2[!BreaksLogicVector]
                               },
                               
                               removeShortMeasurements = function() {
                                 ShortLogicVector = vector ()
                                 v = sapply(self$get_lob(), function(x) {
                                   return(nrow(x$file))
                                 }
                                 )
                                 ShortLogicVector = v >= (self$perday*2)
                                 private$lob2 = private$lob2[ShortLogicVector]
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
                               lob2 = NA,
                               beforetrim = NA,
                               aftertrim = NA,
                               headers = NA,
                               
                               readCSVs = function (FileNames = NULL, dir = getwd(), ext = self$extension, separator = self$separator, skipnum = self$headnrows) {
                                 if (is.null(FileNames)) FileNames = list.files (dir, pattern = paste('*', ext, sep = ''), full.names = TRUE)
                                 if (ext == '.xlsx' || ext == '.xls') {
                                   ListOfDfs = lapply (FileNames, read.xlsx, sheetIndex = 1, header = FALSE, stringsAsFactors = F, startRow = skipnum)
                                 } else {
                                   ListOfDfs = lapply (FileNames, fread, header = FALSE, skip = skipnum)
                                   return (ListOfDfs)
                                 }
                               },
                               
                               readHeaders = function (FileNames = NULL, dir = getwd(), ext = self$extension, separator = self$separator, skipnum = self$headnrows) {
                                 if (is.null(FileNames)) FileNames = list.files (dir, pattern = paste('*', ext, sep = ''), full.names = TRUE)
                                 if (ext == '.xlsx' || ext == '.xls') {
                                   ListOfDfs = lapply (FileNames, function(x) {
                                     data = read.xlsx(x, sheetIndex = 1, header = FALSE, startRow = 1, endRow = skipnum, stringsAsFactors = F)
                                     return(data)
                                               })
                                 } else {
                                   ListOfDfs = lapply (FileNames, fread, header = FALSE, nrows = skipnum)
                                   
                                 }
                                 return (ListOfDfs)
                               },
                               
                               trimDf = function (df, header, dtcol = self$dtcol, datecol = self$datecol, timecol = self$timecol, glucosecol = self$glucosecol) {
                                 #id = as.character(df[self$idrow[[1]], self$idcol[[1]]])
                                 header = as.data.frame(header)
                                 df = as.data.frame(df)
                                 
                                
                                 id = as.character(header[self$idrow[[1]], self$idcol[[1]]])
                                 
                                 #print(head(df))
                                 #print(id)
                                 if(is.na(dtcol)) {
                                   dtcol = ncol(df)+1
                                   df = private$joinDateAndTime(df, datecol = datecol, timecol = timecol, dtcol = dtcol)
                                 }
                                 
                                 
                                 NewDf = df[self$headnrows:nrow(df),]
                                 if(self$extension == ".xlsx" || self$extension == ".xls") {
                                   glucose = NewDf[, paste0("X", as.character(glucosecol))]
                                   NewDf = data.frame(NewDf[,dtcol],glucose)
                                 } else {
                                 NewDf = NewDf[,c(dtcol,glucosecol)]
                                 }
                                 
                                 norows = nrow(NewDf)-10
                                 
                                 NewDf = NewDf[1:norows,]
                                 rownames (NewDf) = NULL
                                 NewDf[1,3] = id
                                 
                                 colnames(NewDf) = c('DT', 'Glucose')
                                 
                                 return (NewDf)
                               },
                               
                               joinDateAndTime = function (df, datecol, timecol, dtcol) {
                                 df[,dtcol] = paste (df[,datecol], df[,timecol])
                                 return (df)
                               },
                               
                               trimAll = function (file = private$beforetrim, header = private$headers) {
                                 # aftertrim = lapply (file, private$trimDf)
                                 aftertrim = vector("list", length(file))
                                 for(i in 1:length(file)) {
                                   res = private$trimDf(file[[i]], header[[i]])
                                   aftertrim[[i]] = res
                                 }
                                 
                                 return (aftertrim)
                               }
                               
                               
                               
                             )
)

###############################
Calculate1 = R6Class ('Calculate1',
                      public = list (
                        
                        
                        initialize = function (Meas) {
                          private$Measurement = Meas
                          # print(private$Measurement$file)
                          rownames(private$Output) = Meas$id
                          colnames(private$Output) = 'Average tests per day'
                        },
                        
                        getMeasurement = function () {
                          return (private$Measurement)
                        },
                        
                        getOutput = function() {
                          self$find_blocks()
                          private$calculateNoNAs()
                          self$calculateWithNas(name = "_whole")
                          self$calculateWithNas(df = private$df_night, name = "_night")
                          self$calculateWithNas(df = private$df_wake, name = "_wake")
                          # self$calculateWithNas(df = private$df_morning, name = "_morning")
                          # self$calculateWithNas(df = private$df_afternoon, name = "_afternoon")
                          self$calculateEverything()
                          
                          return (as.data.frame(private$Output))
                        },
                        
                        calculateEverything = function (df = private$Measurement$file) {
                          private$calculateNoDaysAndNoRecords(df = df)
                          if (private$NoDays >= 2) {
                            private$calculateMean(df = df)
                            private$calculateSD(df = df)
                            private$calculateMedian(df = df)
                            private$calculateCV(df = df)
                            private$calculateBGI(df = df)
                            private$calculateA1c(df = df)
                            private$calculateAUC(df = df)
                            private$calculateM100(df = df)
                            private$calculateJ(df = df)
                            private$calculateMAGE(df = df)
                            private$calculateMODD(df = df)
                            private$calculateCONGA1h(df = df)
                            private$calculateCONGA2h(df = df)
                            private$calculateCONGA3h(df = df)
                            private$calculateCONGA4h(df = df)
                            private$calculateCONGA6h(df = df)
                            private$calculateHypo(df = df)
                            private$calculateHyper(df = df)
                            private$calculateGRADE(df = df)
                          } else {
                            # cat ("Insufficient number of measurement time points (needed at least 576) to calculate parameters in file", private$Measurement$id,".\n", sep = ' ')
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
                            private$Output$GRADE = NA
                            private$Output$GRADE_hypo_percent = NA
                            private$Output$GRADE_eu_percent = NA
                            private$Output$GRADE_hyper_percent = NA
                          }
                        },
                        
                        calculateWithNas = function (df = private$Measurement$filenas, name) {
                          if (T) {
                            private$calculateMean(df = df, name = name)
                            private$calculateMedian(df = df, name = name)
                            private$calculateSD(df = df, name = name)
                            private$calculateCV(df = df, name = name)
                            private$calculateBGI(df = df, name = name)
                            private$calculateA1c(df = df, name = name)
                            private$calculateAUC(df = df, name = name)
                            private$calculateM100(df = df[!is.na(df$Glucose),], name = name)
                            private$calculateJ(df = df, name = name)
                            private$calculateHypo(df = df[!is.na(df$Glucose),], name = name)
                            private$calculateHyper(df = df[!is.na(df$Glucose),], name = name)
                            private$calculateGRADE(df = df[!is.na(df$Glucose),], name = name)
                          } else {
                            # cat ("Insufficient number of measurement time points (needed at least 576) to calculate parameters in file", private$Measurement$id,".\n", sep = ' ')
                            private$Output$Mean = NA
                            private$Output$SD = NA
                            private$Output$Median = NA
                            private$Output$CV = NA
                            private$Output$CV = NA
                            private$Output$M100 = NA
                            private$Output$J = NA
                            private$Output$Percent_of_measurements_below_70mgdl = NA
                            private$Output$Percent_of_measurements_over_180mgdl = NA
                            private$Output$GRADE = NA
                          }
                        },
                        
                        find_blocks = function (df = private$Measurement$filenas) {
                          night = which(hour(df$DT) %in% night_block)
                          private$df_night = df[night,]
                          
                          morning = which(hour(df$DT) %in% morning_block)
                          private$df_morning = df[morning,]
                          
                          afternoon = which(hour(df$DT) %in% afternoon_block)
                          private$df_afternoon = df[afternoon,]
                          
                          wake = c(morning, afternoon)
                          private$df_wake = df[wake, ]
                        }
                      ),
                      private = list (
                        Measurement = NULL,
                        Output = data.frame (matrix(nrow = 1)),
                        NoDays = NULL,
                        NoRecords = NULL,
                        ExcursionLimit = numeric(),
                        df_night = NULL,
                        df_morning = NULL,
                        df_afternoon = NULL,
                        df_wake = NULL,
                        
                        calculateNoNAs = function (df = private$Measurement$filenas, name = "") {
                          norows = nrow(df)
                          noNAs = sum(is.na(df$Glucose))
                          percent = 100 * (norows - noNAs) / norows
                          
                          name = paste0("Average tests per day", name)
                          private$Output[[name]] = percent
                        },
                        
                        calculateNoDaysAndNoRecords = function (df) {
                          NoDays = floor(nrow(df)/private$Measurement$perday)
                          private$NoDays = NoDays
                          #IMPORTANT: next line is setting the days to calculate
                          private$NoRecords = nrow (df)
                          private$Output[["Number of measurements"]] = private$NoRecords
                        },
                        
                        calculateMean = function(df, name = "") {
                          Mean = mean(df$Glucose, na.rm = TRUE)
                          name = paste0("Mean", name)
                          private$Output[[name]] = Mean
                        },
                        
                        calculateSD = function(df, name = "") {
                          SD = sd(df$Glucose, na.rm = TRUE)
                          name = paste0("SD", name)
                          private$Output[[name]] = SD
                          private$ExcursionLimit = SD
                        },
                        
                        calculateMedian = function(df, name = "") {
                          Median = median(df$Glucose, na.rm = TRUE)
                          name = paste0("Median", name)
                          private$Output[[name]] = Median
                        },
                        
                        calculateCV = function(df, name = "") {
                          CV = 100 * (sd(df$Glucose, na.rm = TRUE)/mean(df$Glucose, na.rm = TRUE))
                          name = paste0("CV", name)
                          private$Output[[name]] = CV
                        },
                        
                        calculateM100 = function(df, name = "") {
                          M100 = mean(1000*abs(log(df$Glucose/100, 10)))
                          name = paste0("M100", name)
                          private$Output[[name]] = M100
                        },
                        
                        calculateJ = function(df, name = "") {
                          Mean = mean(df$Glucose, na.rm = TRUE)
                          SD = sd(df$Glucose, na.rm  = TRUE)
                          J = 0.001*(Mean + SD)*(Mean + SD)
                          name = paste0("J", name)
                          private$Output[[name]] = J
                        },
                        
                        calculateMAGE = function(df, name = "") {
                          v = df$Glucose
                          
                          if(max(v) - min(v) <= private$ExcursionLimit) { 
                            private$Output$MAGE = "There are no excursion in the file." 
                            return(NULL) 
                          }
                          
                          #getting turning points and local minima maxima
                          smoothed = private$moving9PF(v)
                          minmax = private$identifyMinMax(smoothed)
                          mins = minmax[[1]]
                          maxs = minmax[[2]]
                          localminmax = private$identifyLocalMinMax(v, mins = mins, maxs = maxs)
                          lmins = localminmax[[1]]
                          lmaxs = localminmax[[2]]
                          
                          #deleting turning points with uncountable excursions on both sides
                          for (i in 1:5) {
                            if (private$areUncountableExcursions(smoothed, mins, maxs) == TRUE) {
                              output = private$removeUncountableTurningPoints(smoothed = smoothed, original = v, mins = mins, maxs = maxs, lmins = lmins, lmaxs = lmaxs)
                              mins = output[[1]]
                              maxs = output[[2]]
                              output = private$removeNotTurningPoints(smoothed = smoothed, mins = mins, maxs = maxs)
                              mins = output[[1]]
                              maxs = output[[2]]
                            }
                          }
                          
                          #deleting turning points with uncountable exursion on one side
                          for (i in 1:5) {
                            if (private$areUncountableExcursions(smoothed, mins, maxs) == TRUE) {
                              
                              output = private$removeUncountableTurningPointsOneExc(smoothed = smoothed, original = v, mins = mins, maxs = maxs, lmins = lmins, lmaxs = lmaxs)
                              mins = output[[1]]
                              maxs = output[[2]]
                              output = private$removeNotTurningPoints(smoothed = smoothed, mins = mins, maxs = maxs)
                              mins = output[[1]]
                              maxs = output[[2]]
                            }
                          }
                          
                          #removing uncountable excursions at the beginning or end
                          output = private$removeUncountableExcFromBegAndEnd(smoothed = smoothed, mins = mins, maxs = maxs)
                          mins = output[[1]]
                          maxs = output[[2]]
                          
                          logic = private$areUncountableExcursions(smoothed = smoothed, mins = mins, maxs = maxs)
                          
                          if(logic == FALSE) {
                            MAGE = private$calculateAmplitudes(vector = v, mins = mins, maxs = maxs)
                            name = paste0("MAGE", name)
                            private$Output[[name]] = MAGE
                          } else {
                            private$Output$MAGE = "Unable to calculate MAGE. Visual analysis should be performed."
                          }
                        },
                        
                        calculateMODD = function(df, name = "") {
                          DayIntervalDiff = vector()
                          v = df$Glucose
                          for (i in seq.int (length.out = length(v)/2)){
                            DayIntervalDiff = append(DayIntervalDiff, abs(v[i] - v[i+private$Measurement$perday]))
                          }
                          #printing DayIntervalDiff
                          #cat(DayIntervalDiff)
                          MODD = mean (DayIntervalDiff)
                          name = paste0("MODD", name)
                          private$Output[[name]] = MODD
                        },
                        
                        calculateCONGA1h = function(df, name = "") {
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
                          name = paste0("CONGA1h", name)
                          private$Output[[name]] = CONGA
                        },
                        
                        calculateCONGA2h = function(df, name = "") {
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
                          name = paste0("CONGA2h", name)
                          private$Output[[name]] = CONGA
                        },
                        
                        calculateCONGA3h = function(df, name = "") {
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
                          name = paste0("CONGA3h", name)
                          private$Output[[name]] = CONGA
                        },
                        
                        calculateCONGA4h = function(df, name = "") {
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
                          name = paste0("CONGA4h", name)
                          private$Output[[name]] = CONGA
                        },
                        
                        calculateCONGA6h = function(df, name = "") {
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
                          name = paste0("CONGA6h", name)
                          private$Output[[name]] = CONGA
                        },
                        
                        calculateHypo = function (df, name = "") {
                          Glucose = as.vector(df$Glucose)
                          Percent = 100 * sum (Glucose < 70)/length (Glucose)
                          # PrettyPercent = format (Percent, nsmall = 2, digits = 2, width = 4)
                          name = paste0("Time spent below 70 mg/dl", name)
                          private$Output[[name]] = Percent
                        },
                        
                        calculateHyper = function (df, name = "") {
                          Glucose = as.vector(df$Glucose)
                          Percent = 100 * sum (Glucose > 180)/length (Glucose)
                          # PrettyPercent = format (Percent, nsmall = 2, digits = 2, width = 4)
                          name = paste0("Time spent over 180 mg/dl", name)
                          private$Output[[name]] = Percent
                        },
                        
                        calculateSlope1 = function () {
                          Glucose = as.vector(df$Glucose)
                          alpha1 = DFA(Glucose, scale.min = 2, scale.max = private$Measurement$perday/12)[[1]]
                          private$Output$Alpha1_DFA = alpha1
                        },
                        
                        calculateSlope2 = function() {
                          Glucose = as.vector (df$Glucose)
                          alpha2 = DFA(Glucose, scale.min = private$Measurement$perday/12, scale.max = private$Measurement$perday/4)[[1]]
                          private$Output$Alpha2_DFA = alpha2
                        },
                        
                        calculateSlope3 = function() {
                          Glucose = as.vector (df$Glucose)
                          alpha3 = DFA(Glucose, scale.min = private$Measurement$perday/4, scale.max = private$Measurement$perday)[[1]]
                          private$Output$Alpha3_DFA = alpha3
                        },
                        
                        moving9PF = function (v) {
                          smoothed = v
                          for (i in seq.int(from = 5, to = length(smoothed)-4)) {
                            smoothed[i] = (sum(v[(i-4):(i+4)]))/9
                          }
                          
                          smoothed[1] = sum(v[1:5])/5
                          smoothed[2] = sum(v[1:6])/6
                          smoothed[3] = sum(v[1:7])/7
                          smoothed[4] = sum(v[1:8])/8
                          smoothed[length(v)-3] = sum(v[(length(v)-7):length(v)])/8
                          smoothed[length(v)-2] = sum(v[(length(v)-6):length(v)])/7
                          smoothed[length(v)-1] = sum(v[(length(v)-5):length(v)])/6
                          smoothed[length(v)] = sum(v[(length(v)-4):length(v)])/5
                          return(smoothed)
                        },
                        
                        identifyMinMax = function(v) {
                          logic = logical()
                          Mins = numeric()
                          Maxs = numeric()
                          up=2
                          
                          if (v[1] > v[2]) {Maxs = append(Maxs, 1)} 
                          if (v[1] < v[2]) {Mins = append(Mins, 1)}
                          for (i in seq.int(length.out = (length(v)-1))) {
                            if (v[i] - v[i+1] > 0) {
                              if (up == 1) Maxs = append(Maxs, i)
                              up = 0
                            } else if (v[i] - v[i+1] < 0) {
                              if (up == 0) Mins = append(Mins, i)
                              up = 1
                            }
                          }
                          if (v[length(v)] > v[length(v)-1]) {Maxs = append(Maxs, length(v))}
                          if (v[length(v)] < v[length(v)-1]) {Mins = append(Mins, length(v))}
                          return(list(v1=Mins,v2=Maxs))
                        },
                        
                        identifyLocalMinMax = function(v, mins, maxs) {
                          LocalMins = numeric()
                          LocalMaxs = numeric()
                          mins = mins
                          maxs = maxs
                          
                          for (i in seq.int(length.out = length(maxs)-1)) {
                            LocalMins = append(LocalMins, which.min(v[maxs[i]:maxs[i+1]])+maxs[i]-1)
                          }
                          for (i in seq.int(length.out = length(mins)-1)) {
                            LocalMaxs = append(LocalMaxs, which.max(v[mins[i]:mins[i+1]])+mins[i]-1)
                          }
                          
                          return(list(LocalMins, LocalMaxs))
                        },
                        
                        removeUncountableTurningPoints = function (smoothed, original, mins, maxs, lmins, lmaxs, limit = private$ExcursionLimit) {
                          smoothed = smoothed
                          original = original
                          mins = mins
                          maxs = maxs
                          lmins = lmins
                          lmaxs = lmaxs
                          limit = limit
                          
                          newmins = mins
                          newmaxs = maxs
                          
                          for (i in 2:(min(length(mins),length(maxs))-(length(mins)==length(maxs))*1)) {
                            #lower index, checking for meaningful excursions on both sides
                            LowInd = min(mins[i], maxs[i]) 
                            LowIndDownExc = abs(smoothed[LowInd] - smoothed[max(maxs[i-1], mins[i-1])])
                            LowIndUpExc = abs(smoothed[mins[i]] - smoothed[maxs[i]])
                            if(LowIndDownExc < limit && LowIndUpExc < limit) {
                              #finding out whether LowInd is a min
                              if (LowInd == mins[i]) {
                                #finding adjacent local minima
                                lower = Position(f = function(x) {x < LowInd}, x = lmins, nomatch = F, right = T)
                                upper = Position(f = function(x) {x > LowInd}, x = lmins, nomatch = F, right = F)
                                #print(c('lower upper', lower, upper))
                                #checking whether position is out of bounds
                                if (lower != F && upper != F) {
                                  #checking whether the minima are higher than the mins[i]
                                  if (original[lmins[lower]] > smoothed[LowInd] && original[lmins[upper]] > smoothed[LowInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmins[i] = NA
                                  }
                                }
                              } else {
                                #LowInd is a max
                                lower = Position(f = function(x) {x < LowInd}, x = lmaxs, nomatch = F, right = T)
                                upper = Position(f = function(x) {x > LowInd}, x = lmaxs, nomatch = F)
                                if (lower != F && upper != F) {
                                  #checking whether the maxima are lower than the maxs[i]
                                  if (original[lmaxs[lower]] < smoothed[LowInd] && original[lmaxs[upper]] < smoothed[LowInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmaxs[i] = NA
                                  }
                                }
                              }
                            }
                            
                            #higher index checking for meaningful excursions on both sides
                            HighInd = max(mins[i], maxs[i]) 
                            HighIndUpExc = abs(smoothed[HighInd] - smoothed[min(maxs[i+1], mins[i+1], na.rm = T)])
                            HighIndDownExc = abs(smoothed[mins[i]] - smoothed[maxs[i]])
                            if(HighIndDownExc < limit && HighIndUpExc < limit) {
                              #finding out whether LowInd is a min
                              if (HighInd == mins[i]) {
                                #finding adjacent local minima
                                lower = Position(f = function(x) {x < HighInd}, x = lmins, nomatch = F, right = T)
                                upper = Position(f = function(x) {x > HighInd}, x = lmins, nomatch = F, right = F)
                                #checking whether position is out of bounds
                                if (lower != F && upper != F) {
                                  #checking whether the minima are higher than the mins[i]
                                  #print (c('are adjacent minima higher',original[lower] > smoothed[HighInd] && original[upper] > smoothed[HighInd]))
                                  if (original[lmins[lower]] > smoothed[HighInd] && original[lmins[upper]] > smoothed[HighInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmins[i] = NA
                                  }
                                }
                              } else {
                                #HighInd is a max
                                lower = Position(f = function(x) {x < HighInd}, x = lmaxs, nomatch = F, right = T)
                                upper = Position(f = function(x) {x > HighInd}, x = lmaxs, nomatch = F)
                                if (lower != F && upper != F) {
                                  #checking whether the maxima are lower than the maxs[i]
                                  if (original[lmaxs[lower]] < smoothed[HighInd] && original[lmaxs[upper]] < smoothed[HighInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmaxs[i] = NA
                                  }
                                }
                              }
                            }
                          }
                          
                          newmins = as.vector(na.omit(newmins))
                          newmaxs = as.vector(na.omit(newmaxs))
                          return(list(newmins, newmaxs))
                        },
                        
                        removeNotTurningPoints = function (smoothed, mins, maxs) {
                          smoothed = smoothed
                          mins = mins
                          maxs = maxs
                          newmins = numeric()
                          newmaxs = numeric()
                          
                          tps = sort.int (c(mins,maxs))
                          newtps = tps
                          for (i in 2:(length(tps)-1)) {
                            triad = c(smoothed[tps[i-1]], smoothed[tps[i]], smoothed[tps[i+1]])
                            if (all(triad == cummax(triad)) || all(triad == cummin(triad))) {
                              newtps[i] = NA
                            }
                          }
                          
                          newtps = as.vector(na.omit(newtps))
                          if(newtps[1]>newtps[2]) {
                            newmaxs = newtps[c(T,F)]
                            newmins = newtps[c(F,T)]
                          } else {
                            newmaxs = newtps[c(F,T)]
                            newmins = newtps[c(T,F)]
                          }
                          
                          return (list(newmins,newmaxs))
                        },
                        
                        removeUncountableTurningPointsOneExc = function (smoothed, original, mins, maxs, lmins, lmaxs, limit = private$ExcursionLimit) {
                          smoothed = smoothed
                          original = original
                          mins = mins
                          maxs = maxs
                          lmins = lmins
                          lmaxs = lmaxs
                          limit = limit
                          
                          newmins = mins
                          newmaxs = maxs
                          if(length(mins) < 2 || length(maxs) < 2) { return (list(mins,maxs))}
                          for (i in 2:(min(length(mins),length(maxs))-(length(mins)==length(maxs))*1)) {
                            #lower index, checking for meaningful excursions on both sides
                            LowInd = min(mins[i], maxs[i]) 
                            LowIndDownExc = abs(smoothed[LowInd] - smoothed[max(maxs[i-1], mins[i-1])])
                            LowIndUpExc = abs(smoothed[mins[i]] - smoothed[maxs[i]])
                            if(LowIndDownExc < limit || LowIndUpExc < limit) {
                              #finding out whether LowInd is a min
                              if (LowInd == mins[i]) {
                                #finding adjacent local minima
                                lower = Position(f = function(x) {x < LowInd}, x = lmins, nomatch = F, right = T)
                                upper = Position(f = function(x) {x > LowInd}, x = lmins, nomatch = F, right = F)
                                if (lower != F && upper != F) {
                                  #checking whether the minima are higher than the mins[i]
                                  #print (c(original[lmins[lower]], smoothed[LowInd], original[lmins[upper]], smoothed[LowInd]))
                                  if (original[lmins[lower]] > smoothed[LowInd] && original[lmins[upper]] > smoothed[LowInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmins[i] = NA
                                  }
                                } else {
                                  if (i == 2 && original[lmins[upper]] > smoothed[LowInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmins[i] = NA
                                  }
                                }
                              } else {
                                #LowInd is a max
                                lower = Position(f = function(x) {x < LowInd}, x = lmaxs, nomatch = F, right = T)
                                upper = Position(f = function(x) {x > LowInd}, x = lmaxs, nomatch = F)
                                if (lower != F && upper != F) {
                                  #checking whether the maxima are lower than the maxs[i]
                                  if (original[lmaxs[lower]] < smoothed[LowInd] && original[lmaxs[upper]] < smoothed[LowInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmaxs[i] = NA
                                  }
                                } else {
                                  #contingency for border cases
                                  #print (c(original[lmaxs[upper]], smoothed[HighInd]))
                                  if (i == 2 && original[lmaxs[upper]] < smoothed[HighInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmaxs[i] = NA
                                  }
                                }
                              }
                            }
                            
                            #higher index checking for meaningful excursions on both sides
                            HighInd = max(mins[i], maxs[i]) 
                            HighIndUpExc = abs(smoothed[HighInd] - smoothed[min(maxs[i+1], mins[i+1], na.rm = T)])
                            HighIndDownExc = abs(smoothed[mins[i]] - smoothed[maxs[i]])
                            if(HighIndDownExc < limit || HighIndUpExc < limit) {
                              #finding out whether LowInd is a min
                              if (HighInd == mins[i]) {
                                #finding adjacent local minima
                                lower = Position(f = function(x) {x < HighInd}, x = lmins, nomatch = F, right = T)
                                upper = Position(f = function(x) {x > HighInd}, x = lmins, nomatch = F, right = F)
                                #checking whether position is out of bounds
                                if (lower != F && upper != F) {
                                  #checking whether the minima are higher than the mins[i]
                                  if (original[lmins[lower]] > smoothed[HighInd] && original[lmins[upper]] > smoothed[HighInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmins[i] = NA
                                  }
                                } else {
                                  if (i == 1 && original[lmins[upper]] > smoothed[LowInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmins[i] = NA
                                  }
                                }
                              } else {
                                #HighInd is a max
                                lower = Position(f = function(x) {x < HighInd}, x = lmaxs, nomatch = F, right = T)
                                upper = Position(f = function(x) {x > HighInd}, x = lmaxs, nomatch = F)
                                #print (c('lower uppper', lower, upper,'checking if upper and lower exist',lower != F && upper != F))
                                if (lower != F && upper != F) {
                                  #checking whether the maxima are lower than the maxs[i]
                                  #print(c(original[lmaxs[lower]] < smoothed[HighInd] && original[lmaxs[upper]] < smoothed[HighInd]))
                                  if (original[lmaxs[lower]] < smoothed[HighInd] && original[lmaxs[upper]] < smoothed[HighInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmaxs[i] = NA
                                  }
                                } else {
                                  #contingency for border cases
                                  #print(c('FALSE here means cutting',i == min(length(mins),length(maxs))-(length(mins)==length(maxs))*1,original[lmaxs[lower]] < smoothed[HighInd]))
                                  if (i == min(length(mins),length(maxs))-(length(mins)==length(maxs))*1 && original[lmaxs[lower]] < smoothed[HighInd]) {
                                    
                                  } else {
                                    #removing the turning point from a newmins vector
                                    newmaxs[i] = NA
                                  }
                                }
                              }
                            }
                          }
                          
                          newmins = as.vector(na.omit(newmins))
                          newmaxs = as.vector(na.omit(newmaxs))
                          return(list(newmins, newmaxs))
                        },
                        
                        removeUncountableExcFromBegAndEnd = function (smoothed, mins, maxs, limit = private$ExcursionLimit) {
                          smoothed = smoothed
                          mins = mins
                          maxs = maxs
                          limit = limit
                          
                          
                          LowIndBeg = min(mins[1], maxs[1])
                          HighIndBeg = max(mins[1], maxs[1])
                          HighIndEnd = max(mins[length(mins)], maxs[length(maxs)])
                          LowIndEnd = min(mins[length(mins)], maxs[length(maxs)])
                          
                          #print(limit)
                          #print(abs(smoothed[LowIndBeg] - smoothed[HighIndBeg]))
                          #print(abs(smoothed[LowIndBeg] - smoothed[HighIndBeg])<limit)
                          if (abs(smoothed[LowIndBeg] - smoothed[HighIndBeg])<limit) {
                            if(LowIndBeg == mins[1]) {
                              mins = mins[-1]
                            } else {
                              maxs = maxs[-1]
                            }
                          }
                          
                          #print(c(abs(smoothed[HighIndEnd] - smoothed[LowIndEnd]),abs(smoothed[HighIndEnd] - smoothed[LowIndEnd])<limit))
                          if (abs(smoothed[HighIndEnd] - smoothed[LowIndEnd])<limit) {
                            if (HighIndEnd == mins[length(mins)]) {
                              mins = mins[-length(mins)]
                            } else {
                              maxs = maxs[-length(maxs)]
                            }
                          }
                          
                          return (list(mins, maxs))
                        },
                        
                        areUncountableExcursions = function (smoothed, mins, maxs, limit = private$ExcursionLimit) {
                          smoothed = smoothed
                          mins = mins
                          maxs = maxs
                          limit = limit
                          tps = sort.int(c(mins,maxs))
                          diffs = vector(mode = "numeric", length = length(tps)-1)
                          
                          for (i in 1:(length(tps)-1)) {
                            diffs[i] = abs(smoothed[tps[i]] - smoothed[tps[i+1]])
                          }
                          
                          logic = all(diffs>limit)
                          
                          #print(c(diffs, logic, limit))
                          return (!logic)
                        },
                        
                        calculateAmplitudes = function (vector, mins, maxs) {
                          v = vector
                          mins = mins
                          maxs = maxs
                          tps = sort.int(c(mins,maxs))
                          diffs = length(tps)-1
                          for (i in seq.int(length.out = length(tps)-1)) {
                            diffs[i] = abs(v[tps[i]]-v[tps[i+1]])
                          }
                          
                          out = mean(diffs)
                          return(out)
                        },
                        
                        findIndOfFirstExcursion = function (v, limit = private$ExcursionLimit) {
                          v = v
                          limit = limit
                          diff = vector (mode = 'numeric', length = length (v)-1)
                          for (i in seq.int(length.out = length(v)-1)) {
                            diff[i] = abs(v[i]-v[i+1])
                          }
                          
                          Ind = Position (f = function(x) {x>limit}, diff)
                          return (Ind)
                        },
                        
                        calculateGRADE = function (df, name = "") {
                          Glucose = as.vector(df$Glucose)
                          GRADEs = 425 * ((log10(log10(Glucose/18)) + 0.16)^2)
                          GRADE = mean(GRADEs)
                          namea = paste0("GRADE", name)
                          private$Output[[namea]] = GRADE
                          
                          #calculating GRADE hypoglycaemia percent
                          hypos = which(Glucose < 90)
                          HypoPercent = 100*sum(GRADEs[hypos])/sum(GRADEs)
                          namea = paste0("GRADE_hyp", name)
                          private$Output[[namea]] = HypoPercent
                          
                          #calculating GRADE euglycaemia percent
                          eus = which (Glucose>=90 & Glucose<=140)
                          EuPercent = 100*sum(GRADEs[eus])/sum(GRADEs)
                          namea = paste0("GRADE_eu", name)
                          private$Output[[namea]] = EuPercent
                          
                          #calculating GRADE hyperglycaemia percent
                          hypers = which(Glucose > 140)
                          HyperPercent = 100*sum(GRADEs[hypers])/sum(GRADEs)
                          namea = paste0("GRADE_hyper", name)
                          private$Output[[namea]] = HyperPercent
                        },
                        
                        calculateBGI = function (df, name = "") {
                          Glucose = df$Glucose[!is.na(df$Glucose)]
                          f_Glucose = 1.509 * ((log(Glucose) ^ 1.084) - 5.381)
                          r_Glucose = 10 * (f_Glucose ^ 2)
                          
                          LBGI = mean(r_Glucose[f_Glucose > 0])
                          HBGI = mean(r_Glucose[f_Glucose < 0])
                          
                          namea = paste0("LBGI", name)
                          nameb = paste0("HBGI", name)
                          
                          private$Output[[namea]] = LBGI
                          private$Output[[nameb]] = HBGI
                        },
                        
                        calculateA1c = function (df, name = "") {
                          Glucose = df$Glucose[!is.na(df$Glucose)]
                          Glucose = Glucose / 18.02
                          eA1c = (mean(Glucose) + 2.52)/1.583
                          name = paste0("eA1c", name)
                          private$Output[[name]] = eA1c
                          
                        },
                        
                        calculateAUC = function (df, name = "", interval = private$Measurement$interval) {
                          Glucose = df$Glucose[!is.na(df$Glucose)]
                          x = seq(from = 0, length.out = length(Glucose), by = interval)
                          AUC = MESS::auc(x = x, y = Glucose, type = "linear")/(length(Glucose)/(private$Measurement$perday/24))
                          name = paste0("AUC", name, "[h * glucose]")
                          private$Output[[name]] = AUC
                        }
                        
                      ),
                      active = list (
                        
                      )
)

