'use strict';

/**
 * Utility function module.
 * @module util
 */

var Coordinate = require('./coordinate');

/**
 * Load images and defined by object and invoke callback when completed.
 *
 * @param {Object} sources A dictionary of sources to load.
 * @param {function} callback A callback function to call with image dict.
 */
exports.loadImages = function(sources, callback) {
  var images = {}, imagesLeft = 0;

  for(var src in sources) // count non-false properties as images
    if(sources.hasOwnProperty(src) && sources[src])
      imagesLeft++;

  var countdown = function() {
    if(--imagesLeft <= 0) {
      callback(images);
    }
  };

  for(src in sources) { // load non-false properties to images object
    if(sources.hasOwnProperty(src) && sources[src]) {
      /* global Image */
      images[src] = new Image();
      images[src].onload = countdown;
      images[src].src = sources[src];
    }
  }
};

/**
 * Helper function to create coordinates for standard handicap placement.
 *
 * @param {int} size Board size (9, 13, 19 supported).
 * @param {itn} num Number of handicap stones.
 * @returns {Array} Array of Coordinate objects.
 */
exports.getHandicapCoordinates = function(size, num) {
  // Telephone dial style numbering
  var handicapPlaces = [[], [], [3,7], [3,7,9], [1,3,7,9], [1,3,5,7,9],
      [1,3,4,6,7,9], [1,3,4,5,6,7,9], [1,2,3,4,6,7,8,9],
      [1,2,3,4,5,6,7,8,9]];
  var places = handicapPlaces[num], offset = (size <= 9 ? 2 : 3),
      step = (size - 1) / 2 - offset, coords = [];

  if(places) {
    for(var n=0; n<places.length; n++) {
      var i = (places[n]-1) % 3, j = Math.floor((places[n]-1) / 3);
      coords.push(new Coordinate(offset+i*step, offset+j*step));
    }
  }

  return coords;
};

/**
 * Deep extend an object.
 *
 * @function extend
 * @param {Object} dest Destination object to extend.
 * @param {Object} src Source object which properties will be copied.
 * @returns {Object} Extended destination object.
 */
exports.extend = function(dest, src) {
  for(var key in src) {
    if(src.hasOwnProperty(key)) {
      if(typeof src[key] === 'object') {
        if(!dest[key] || (typeof dest[key] !== 'object'))
          dest[key] = {}; // create/overwrite if necessary
        exports.extend(dest[key], src[key]);
      } else dest[key] = src[key];
    }
  }

  return dest;
};
