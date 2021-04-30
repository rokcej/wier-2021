!function(){"use strict";var n=document,a=window;"function"!=typeof Object.assign&&Object.defineProperty(Object,"assign",{value:function(e){if(null==e)throw new TypeError("Cannot convert undefined or null to object");for(var t=Object(e),i=1;i<arguments.length;i++){var n=arguments[i];if(null!=n)for(var r in n)Object.prototype.hasOwnProperty.call(n,r)&&(t[r]=n[r])}return t},writable:!0,configurable:!0});function t(e){this.siteDomain=e,this.setParams=function(e){this.params=e},this.track=function(){var e;-1===["de","fr","ru"].indexOf(this.siteDomain.toLowerCase())&&("viewcontent"!==(e=new String(this.params.ev).toLowerCase())&&"pageview"!==e&&"addtocart"!==e&&"purchase"!==e||(e=this.buildUrl(this.params),e=(new Image(1,1).src=e).replace("/rt/","/tr/"),new Image(1,1).src=e))},this.buildUrl=function(e){var t,i="https://www."+this.getDomain()+"/rt/?",n=[];for(t in e)e.hasOwnProperty(t)&&n.push(t+"="+encodeURIComponent(e[t]));var r=n.join("&").length;return n.push("l="+r),n.push("v=1"),i+n.join("&")},this.getDomain=function(){var e=a.location.href.match(/([0-9]+)\.devklarka\.[a-z]{2,}/);if(e)return parseInt(e[1],10)+".devklarka."+this.siteDomain.toLowerCase();switch(this.siteDomain.toLowerCase()){case"br":return"glami.com.br";case"tr":return"glami.com.tr";default:return"glami."+this.siteDomain.toLowerCase()}}}var o=function(e){for(var t=e+"=",i=document.cookie.split(";"),n=0;n<i.length;n++){for(var r=i[n];" "===r.charAt(0);)r=r.substring(1,r.length);if(0===r.indexOf(t))return decodeURIComponent(r.substring(t.length,r.length))}return null},s=function(e,t,i,n,r){var a,o="";i&&((a=new Date).setTime(a.getTime()+60*i*1e3),o=a.toUTCString()),document.cookie=[e,"=",encodeURIComponent(t),o&&"; expires="+o,r&&"; path="+r,n&&"; domain="+n].join("")},c=function(){var e=window.location.href.match(/gci=([a-z0-9]{40})/i);if(e&&e[1])return e[1]},h=function(){var e=window.location.search.match(/gclid=([^&#]+)/i);if(e&&e[1])return e[1]},l={sessionCookieLifetime:43200,sessionCookieName:"gp_s",exitIdCookieName:"gp_e",config:{},paramsHashHistory:[],getBeacon:function(e){return new t(e)},create:function(e,t,i,n){i=i||l.DEFAULT_TRACKER_NAME;var r=(n=n||{}).source||l.DEFAULT_SOURCE_NAME,n=this.getCookieDomain(n.cookieDomain||"auto");this.config[i]={},this.config[i].apiKey=e,this.config[i].siteDomain=t||"cz",this.config[i].source=r,this.config[i].domain=n,this.storeExitClickId({gci:c(),gclid:h()},i)},track:function(e,t,i){var n,r,a,o={ev:t};for(a in i)if(i.hasOwnProperty(a)){var s=i[a];if(void 0!==s){if(s.constructor===Array){for(n=0,r=s.length;n<r;n++)s[n]=new String(s[n]).replace(/,/g,"\\,");var c=s.join(",")}else c=s+"";o["cd["+a+"]"]=c.substr(0,1e3)}}var h=this.getExitClickId();h&&(o["cd[gci]"]=h);t=Object.assign(this.getDefaultParams(e),o),h=this.getParamsHash(t);this.eventAlreadySent(h)||((e=this.getBeacon(this.config[e].siteDomain)).setParams(t),e.track(),this.paramsHashHistory.push(h))},getDefaultParams:function(e){var t={};t.k=this.config[e].apiKey,n.referrer&&(t.r=n.referrer),t.sid=this.getSessionId(e),t.u=a.location.href,t.pt=document.title,t.w=a.screen&&a.screen.availWidth?a.screen.availWidth:"",t.h=a.screen&&a.screen.availHeight?a.screen.availHeight:"";var i=Math.round((new Date).getTime()/1e3);return t.ts=i,t["cd[source]"]=this.config[e].source,t},push:function(){var e=Array.prototype.slice.call(arguments),t=e.slice(0,1).toString(),i=e.slice(1),n=l.DEFAULT_TRACKER_NAME;if(-1!==t.indexOf(".")&&(t=(e=t.split(".",2))[1],n=e[0]),this.hasOwnProperty(t))switch(t){case"create":this[t].apply(this,i);break;case"track":this[t].apply(this,[n].concat(i));break;default:console.error('Calling non-standard method "'+t+"'.")}else console.error('Calling non-standard method "'+t+"'.")},getSessionId:function(e){var t=o(this.sessionCookieName);return t&&t.match(/^[0-9]+\.[0-9]+$/)||(t=this.generateSessionId()),s(this.sessionCookieName,t,this.sessionCookieLifetime,this.config[e].domain,"/"),t},generateSessionId:function(){var e=Math.round(+new Date/1e3);return Math.round(Math.random()*e)+"."+e},storeExitClickId:function(e,t){var i=(new Date).valueOf(),n=(o(this.exitIdCookieName)||"").match(/([^;]+)?;(.*)?\.([0-9]+)/),r={gci:"",gclid:""};(e.gci||e.gclid)&&(e.timestamp=i,n&&(r.gci=n[1],r.gclid=n[2],r.timestamp=n[3],!e.gci&&r.gci&&(e.gci=r.gci),!e.gclid&&r.gclid&&(e.gclid=r.gclid),r.timestamp&&(e.timestamp=r.timestamp)),(e.gclid||e.gci)&&(e=(void 0===e.gci?"":e.gci)+";"+(void 0===e.gclid?"":e.gclid)+"."+e.timestamp,s(this.exitIdCookieName,e,this.sessionCookieLifetime,this.config[t].domain,"/")))},getExitClickId:function(){var e=o(this.exitIdCookieName);return e||!1},getParamsHash:function(e){var t,i,n=[];for(t in delete(e=Object.assign({},e)).ts,delete e.sid,e)e.hasOwnProperty(t)&&(i=e[t],n.push(t+":"+i));return n.join()},eventAlreadySent:function(e){for(var t=0,i=this.paramsHashHistory.length;t<i;t++)if(this.paramsHashHistory[t]===e)return!0;return!1},getCookieDomain:function(e){var t="";if("auto"===e){var i=(t=document.domain||location.hostname).split(".");2<i.length&&(t=i.slice(1).join("."))}else{if(null===e.match(/^\.?([a-z0-9]+\.)*[a-z0-9][a-z0-9-]*\.[a-z]{2,6}$/i))throw new Error("Invalid domain "+e+".");t=0===e.indexOf(".")?e.substr(1):e}return t}};l.DEFAULT_TRACKER_NAME="def",l.DEFAULT_SOURCE_NAME="js",function(){var e=a.GlamiTrackerObject||"glami",t=a[e];if(t&&t.q&&t.q.constructor===Array)for(var i=t.q,n=0,r=i.length;n<r;n++)l.push.apply(l,i[n]);a[e]=l.push.bind(l)}()}();