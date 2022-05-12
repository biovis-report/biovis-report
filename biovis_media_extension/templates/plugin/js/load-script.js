function loadScript( url, callback ) {
  var script = document.createElement( "script" )
  script.type = "text/javascript";
  if(script.readyState) {  // only required for IE <9
    script.onreadystatechange = function() {
      if ( script.readyState === "loaded" || script.readyState === "complete" ) {
        script.onreadystatechange = null;
        callback();
      }
    };
  } else {  //Others
    script.onload = function() {
      callback();
    };
  }

  script.src = url;
  document.getElementsByTagName( "head" )[0].appendChild( script );
}

function checkDeps(net_path, ftype, noInject) {
  var allFiles = []
  if (ftype == 'js' || ftype == 'javascript') {
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      if (scripts[i].src) {
        allFiles.push(scripts[i].src)
      }
    }
  } else if (ftype == 'css') {
    var cssLinks = document.getElementsByTagName("link");
    for (var i = 0; i < cssLinks.length; i++) {
      if (cssLinks[i].href) {
        allFiles.push(cssLinks[i].href)
      }
    }
  }

  // net_path: '/pivot-table-js/css/webdatarocks.min.css'
  var full_net_path = window.location.origin + net_path
  var another_net_path = window.location.origin + '/' + net_path
  if (allFiles.indexOf(full_net_path) >= 0 ||
      allFiles.indexOf(net_path) >= 0 ||
      allFiles.indexOf(another_net_path) >= 0) {
      if (noInject) {
        return true
      } else {
        console.log(net_path + ' exists, so webInject skip it.');
      }
  } else {
    if (noInject) {
      return false
    } else {
      if (ftype == 'css') {
          window.webInject.css(net_path, function(){console.log(net_path + ' injected.')})
      } else if (ftype == 'js' || ftype == 'javascript') {
          window.webInject.js(net_path, function(){console.log(net_path + ' injected.')})
      }
    }
  }
};

var Loader = function () { }
Loader.prototype = {
  require: function (scripts, callback) {
    this.loadCount      = 0;
    this.totalRequired  = scripts.length;
    this.callback       = callback;

    var injectedScript = []
    for (var i = 0; i < scripts.length; i++) {
      // Check if the script exists.
      if(checkDeps(scripts[i], ftype='js', noInject=true)) {
        console.log(scripts[i] + ' exists.')
      } else {
        this.writeScript(scripts[i])
        console.log('Wrote ' + scripts[i] + ' successfully.')
        injectedScript.push(scripts[i])
      }
    }

    // All deps exist, so need to call callback manually.
    if (injectedScript.length == 0) {
      this.callback.call();
    }
  },
  loaded: function (evt) {
    this.loadCount++;

    if (this.loadCount == this.totalRequired && typeof this.callback == 'function') this.callback.call();
  },
  writeScript: function (src) {
    if (checkDeps(src, 'js', true)) {
      console.log(src + ' exists.');
    } else {
      var self = this;
      var s = document.createElement('script');
      s.type = "text/javascript";
      s.async = false;
      s.defer = true;
      s.src = src;
      s.addEventListener('load', function (e) { self.loaded(e); }, false);
      var head = document.getElementsByTagName('head')[0];
      head.appendChild(s);
      return true
    }
  }
}