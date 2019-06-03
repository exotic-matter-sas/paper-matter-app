// Used in package.json>jest>moduleNameMapper to mock all worker files (files ending with '.worker.js') as Jest doesn't support them
module.exports = Object.create(null);
