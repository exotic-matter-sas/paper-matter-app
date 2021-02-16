/*
 * Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE in the project root for more information.
 */

// This script is needed to get around a Selenium/Webdriver bug with drag n drop
// ref: https://github.com/SeleniumHQ/selenium/issues/8003

function simulateDragDrop(sourceNode, destinationNode) {
  var EVENT_TYPES = {
    DRAG_END: 'dragend',
    DRAG_START: 'dragstart',
    DROP: 'drop'
  };

  function createCustomEvent(type) {
    var event = new CustomEvent("CustomEvent");
    event.initCustomEvent(type, true, true, null);
    event.dataTransfer = {
      data: {
      },
      setData: function(type, val) {
        this.data[type] = val
      },
      getData: function(type) {
        return this.data[type]
      },
      setDragImage: function(){}
    };
    return event
  }

  function dispatchEvent(node, type, event) {
    if (node.dispatchEvent) {
      return node.dispatchEvent(event)
    }
    if (node.fireEvent) {
      return node.fireEvent("on" + type, event)
    }
  }

  var event = createCustomEvent(EVENT_TYPES.DRAG_START);
  dispatchEvent(sourceNode, EVENT_TYPES.DRAG_START, event);

  var dropEvent = createCustomEvent(EVENT_TYPES.DROP);
  dropEvent.dataTransfer = event.dataTransfer;
  dispatchEvent(destinationNode, EVENT_TYPES.DROP, dropEvent);

  var dragEndEvent = createCustomEvent(EVENT_TYPES.DRAG_END);
  dragEndEvent.dataTransfer = event.dataTransfer;
  dispatchEvent(sourceNode, EVENT_TYPES.DRAG_END, dragEndEvent)
}

// arguments array is auto injected by selenium execute_script command
simulateDragDrop(arguments[0], arguments[1]);
