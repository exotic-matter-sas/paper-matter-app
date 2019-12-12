/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

// Used in package.json>jest>moduleNameMapper to mock all worker files (files ending with '.worker.js') as Jest doesn't support them
module.exports = Object.create(null);
