if ( ! "verb" %in% ls() ) {
  verb=function(...,d=""){print(paste("Verbose:",d));print(c(...))}
} 

verb('sourced verbose.R')
