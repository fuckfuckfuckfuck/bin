showFrame <- function (upn) {
  if (upn < 0) {
    env <- .GLobalEnv
  } else {
    env <- parent.frame(n = upn +1)
  }
  
  vars <- ls(envir=env)
  
  for (vr in vars) {
    vrg <- get(vr, envir = env)
    if (!is.function(vrg)) {
      cat(vr, ":\n", sep="")
      print(vrg)
    }
        
  }
}