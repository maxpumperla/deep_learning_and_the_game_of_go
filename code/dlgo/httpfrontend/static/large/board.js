// Import or create JGO namespace
var JGO = JGO || {};

JGO.BOARD = JGO.BOARD || {};

JGO.BOARD.large = {
    textures: {
        black: 'large/black.png',
        white: 'large/white.png',
        shadow:'large/shadow.png',
        board: 'large/shinkaya.jpg'
    },

    // Margins around the board, both on normal edges and clipped ones
    margin: {normal: 40, clipped: 40},

    // Shadow color, blur and offset
    boardShadow: {color: '#ffe0a8', blur: 30, offX: 5, offY: 5},

    // Lighter border around the board makes it more photorealistic
    border: {color: 'rgba(255, 255, 255, 0.3)', lineWidth: 2},

    // Amount of "extra wood" around the grid where stones lie
    padding: {normal: 20, clipped: 10},

    // Grid color and size, line widths
    grid: {color: '#202020', x: 50, y: 50, smooth: 0.0,
        borderWidth: 1.5, lineWidth: 1.2},

    // Star point radius
    stars: {radius: 3},

    // Coordinate color and font
    coordinates: {color: '#808080', font: 'normal 18px sanf-serif'},

    // Stone radius  and alpha for semi-transparent stones
    stone: {radius: 24, dimAlpha:0.6},

    // Shadow offset from center
    shadow: {xOff: -2, yOff: 2},

    // Mark base size and line width, color and font settings
    mark: {lineWidth: 1.5, blackColor: 'white', whiteColor: 'black',
        clearColor: 'black', font: 'normal 24px sanf-serif'}
};

JGO.BOARD.largeWalnut = JGO.util.extend(JGO.util.extend({}, JGO.BOARD.large), {
    textures: {board: 'large/walnut.jpg', shadow: 'large/shadow_dark.png'},
    boardShadow: {color: '#e2baa0'},
    grid: {color: '#101010', borderWidth: 1.8, lineWidth: 1.5}
});

JGO.BOARD.largeBW = JGO.util.extend(JGO.util.extend({}, JGO.BOARD.large), {
    textures: false
});
