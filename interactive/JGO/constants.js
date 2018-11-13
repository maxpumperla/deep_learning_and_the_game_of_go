'use strict';

var util = require('./util');

/**
 * Enum for intersection types. Aliased in JGO namespace, e.g. JGO.BLACK.
 * @enum
 * @readonly
 */
exports.INTERSECTION = {
  CLEAR: 0,
  /** Black stone */
  BLACK: 1,
  /** White stone */
  WHITE: 2,
  /** Semi-transparent black stone */
  DIM_BLACK: 3,
  /** Semi-transparent white stone */
  DIM_WHITE: 4
};

// Alias all objects into globals
util.extend(exports, exports.INTERSECTION);

/**
 * Enum for marker types.
 * @readonly
 * @enum
 */
exports.MARK = {
  /** No marker ('') */
  NONE: '',
  /** Selected intersection */
  SELECTED: '^',
  /** Square */
  SQUARE: '#',
  /** Triangle */
  TRIANGLE: '/',
  /** Circle */
  CIRCLE: '0',
  /** Cross */
  CROSS: '*',
  /** Black territory */
  BLACK_TERRITORY: '-',
  /** White territory */
  WHITE_TERRITORY: '+'
};

/**
 * Board coordinate array.
 * @constant
 */
exports.COORDINATES = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'.split('');
