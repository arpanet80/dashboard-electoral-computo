(function(window) {
  window["env"] = window["env"] || {};

  /////////////////////////////////////////////////////////////////////////
  // https://pumpingco.de/blog/environment-variables-angular-docker/
  /////////////////////////////////////////////////////////////////////////
  // Environment variables

  /* Local */
  window["env"]["apiUrl"] = "http://localhost:3009/";
  window["env"]["debug"] = true;

})(this);
