/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

// Used in package.json>jest>moduleNameMapper to mock all worker files (files ending with '.worker.js') as Jest doesn't support them
module.exports = Object.create(null);
