# Map to unittesting Vue with Jest

## Basic rules

- Every Vue component (`.vue`) should be tested in a different `.spec.js` file
  
  *eg. `Home.spec.js` should test `Home.vue`*
  
- When you need a fake props or attribute value use `./../tools/testValues.js` module instead of hardcoded values

  eg.
  ```javascript
  import * as tv from './../tools/testValues.js';
  
  ...
  
  wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});

  ```
  
- [shallowMount](https://vue-test-utils.vuejs.org/api/#shallowmount) Vue components to test them

  eg.
  ```javascript
  import {createLocalVue, shallowMount} from '@vue/test-utils';
  import Home from "../../src/views/Home";

  const localVue = createLocalVue(); // to not pollute the global Vue class

  const wrapper = shallowMount(Home, {
    localVue,
    methods: {
      methodName: mockedMethodName, // Add method to mock here
    }
  })

  ```
- [Mock](https://en.wikipedia.org/wiki/Mock_object) every calls to computed, methods, external library: only the logic of the current method should be tested

## What to test and how to test it ?

### 1. Template rendering

**How:** assert main text / html / element / props value is present in template.

```javascript
// text
expect(wrapper.text()).toContain('No document yet');

// html
expect(wrapper.html()).toContain('<div id="app">');

// element
expect(wrapper.find('#app')).toBeThruthy();

// props value in html
Object.values(tv.DOCUMENT_PROPS).forEach(function(documentData){ expect(wrapper.html()).toContain(documentData) });
```

**Utility:** check component/template association and prevent Vue template compilation error (eg. when there is 2 tags at root level).

### 2. Methods

**How:** assert method call proper method(s) / call proper api request / trigger proper event / return proper value / are called by event...

```javascript
// imports here

jest.mock('axios', () => ({ get: jest.fn() }));
const wrapper = shallowMount(TestedComponent, {
  localVue,
  methods: {
    methodA: mockedMethodA,
    methodB: mockedMethodB,
    }
});

// when
const testedReturn = wrapper.vm.testedMethod();

// then call methods
expect(methodA).toHaveBeenCalledTimes(1);
expect(methodA).toHaveBeenCalledWith(specificArg);
expect(methodB).toHaveBeenCalledTimes(1);

// then call api request
await flushPromises(); // test have to be async to use await
expect(axios.get).toHaveBeenCalledTimes(1);
expect(axios.get).toHaveBeenCalledWith('/app/api/v1/documents');

// then trigger event
expect(wrapper.emitted('proper-event')).toBeTruthy();

// then return proper value
expect(testedReturn).toBe('properValue');

// ----------------------
// when (called by event)
wrapper.find(EventsComponent).vm.$emit('tested-event', argEvent);

// then method called
expect(mockedMethodA).toHaveBeenCalledWith(argEvent);
```

**Utility:** check component logic and interactions with other components are not broken.

### 3. Computed

**How:** assert computed return proper value.

```javascript
...
const wrapper = shallowMount(TestedComponent, {
  localVue
});

// when
const testedValue = wrapper.vm.testedComputed;

//then
expect(testedValue).toBe('ComputedValue');
```

**Utility:** check computed logic and returned format.

### 3. Error handling

**How:** assert method error handling is working properly.

```javascript
...
jest.mock('axios', () => ({ get: jest.fn() }));
axios.get.mockRejectedValue('errorDescription');

const wrapper = shallowMount(TestedComponent, {
  localVue,
  methods: {
      mixinAlert: mockedMixinAlert,
    }
});

// when calling method and api request return an error
wrapper.vm.testedMethod();

// then it call mixinAlert to show error to user
await flushPromises(); // test have to be async to use await
expect(mockedMixinAlert).toHaveBeenCalled();
```

**Utility:** check computed logic and returned format.

## `.spec.js` template

To avoid common pitfalls (listed in next section), respect the structure used in `_template.spec.js`.

## Commons pitfalls

TODO finish this section

| Error | Suggested solution |
|-------------------|------------------|
|  |  |