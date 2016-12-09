theme_default = theme(
  
  line = element_line(color = "black", size = 0.75, linetype = 1),
  axis.ticks = element_line(size = 0.2),
  axis.line = element_line(size = 0.75),
  panel.grid = element_blank(),
  
  
  rect = element_rect(color = "transparent", fill = "transparent"),
  panel.background = element_rect(fill = "white", colour = "white"),
  panel.border = element_rect(fill=NA, colour = "black", size = 0.75),
  plot.background = element_rect(),
  
  
  text = element_text(family = , face = "plain"),
  plot.title = element_text(size = 16),
  axis.title = element_text(size = 14, hjust = 0.5, margin = margin(2,2,2,2)),
  axis.title.x = element_text(vjust = 0),
  axis.title.y = element_text(vjust = 0),
  axis.text = element_text(size = 12)
)