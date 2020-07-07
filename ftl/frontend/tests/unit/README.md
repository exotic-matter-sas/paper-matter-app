# Map to unittesting Vue with Jest

## Basic rules

- Every Vue component (`.vue`) should be tested in a different `.spec.js` file

  _eg. `Home.spec.js` should test `Home.vue`_

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
  import { createLocalVue, shallowMount } from "@vue/test-utils";
  import Home from "../../src/views/Home";

  const localVue = createLocalVue(); // to not pollute the global Vue class

  const wrapper = shallowMount(Home, {
    localVue,
    methods: {
      methodName: mockedMethodName, // Add method to mock here
    },
  });
  ```

- [Mock](https://en.wikipedia.org/wiki/Mock_object) every calls to computed, methods, external library: only the logic of the current method should be tested

## What to test and how to test it ?

### 1. Template rendering

**How:** assert main text / html / element / props value is present in template.

```javascript
// text
expect(wrapper.text()).toContain("No document yet");

// html
expect(wrapper.html()).toContain('<div id="app">');

// element
const elementSelector = "#element-id";
const elem = wrapper.find(elementSelector);

expect(elem.is(elementSelector)).toBe(true);

// props value in html
delete tv.DOCUMENT_PROPS.note; // remove unwanted data here
Object.values(tv.DOCUMENT_PROPS).forEach(function (documentData) {
  expect(wrapper.html()).toContain(documentData);
});
```

**Utility:** check component/template association and prevent Vue template compilation error (eg. when there is 2 tags at root level).

### 2. Methods (or watcher)

**How:** assert method call proper method(s) / call proper api request / trigger proper event / return proper value / are called by event...

```javascript
// imports here

jest.mock("axios", () => ({ get: jest.fn() }));
const wrapper = shallowMount(TestedComponent, {
  localVue,
  methods: {
    methodA: mockedMethodA,
    methodB: mockedMethodB,
  },
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
expect(axios.get).toHaveBeenCalledWith("/app/api/v1/documents");

// then return proper value
expect(testedReturn).toBe("properValue");

// then trigger event
await flushPromises(); // test have to be async to use await
expect(wrapper.emitted("proper-event")).toBeTruthy();
expect(wrapper.emitted("proper-event").length).toBe(1);
expect(wrapper.emitted("proper-event")[0]).toEqual(["eventArg1", "eventArg2"]);

// ----------------------
// when (called by event)
wrapper.find(EventsComponent).vm.$emit("tested-event", argEvent);

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
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}});

jest.mock('axios', () => ({ get: jest.fn() }));
axios.get.mockRejectedValue('errorDescription');

const wrapper = shallowMount(TestedComponent, {
  localVue
});

// when calling method and api request return an error
wrapper.vm.testedMethod();

// then it call mixinAlert to show error to user
await flushPromises(); // test have to be async to use await
expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
```

**Utility:** check that all possible errors are properly catched.

## `.spec.js` template

To avoid common pitfalls (listed in next section), respect the structure used in `_template.js`.

## Common pitfalls

| Error                                                                                           | Suggested solution                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cannot read property 'then' of undefined                                                        | A unmock method is probably called by the test, try to add a mock for component method mentioned in stacktrace                                                              |
| Mock return `null` instead of value set with `mockReturnValue`                                  | Check that `mockedMethod.mockReturnValue('value')` is called before shallowMount                                                                                            |
| Mocked method is called too many times                                                          | Check that `jest.clearAllMocks();` line is present after shallowMount to reset mockedMethod.mock.calls counter after `mounted`                                              |
|                                                                                                 | Also check that a unmocked method/computed isn't calling the mocked method, it should be mocked                                                                             |
| [Vue warn]: Unknown custom element: <customElement> - did you register the component correctly? | Call `localVue.use(ElementComponent)` to register the component (eg. BootstrapVue)                                                                                          |
|                                                                                                 | If `localVue.use` isn't possible (eg. it prevent library mocking), add element to stubs option in shallowMount : `stubs: ['customElement']`                                 |
| Props value isn't updated after using wrapper.setData                                           | By default props aren't reactive, unless they are also declared inside `data()` (see [explanations here](https://forum.vuejs.org/t/computed-property-not-updating/21148/6)) |

## Known issues

- `wrapper.setData` cause "[Vue warn]: Avoid mutating a prop directly" warning during test run (no clean solution found to hide this warning for now)
- `wrapper.setComputed` have been removed from vue-test-utils, it prevent us from restoring original computed at the start of the test (like what is done with methods), forcing us to shallowMount component in each test. But there could be better ways to do it, as described here: https://github.com/vuejs/vue-test-utils/issues/331#issuecomment-403087709
- `watcher` seems non mockable (when mocked using [the classic shallowMount options](https://vue-test-utils.vuejs.org/api/options.html#other-options) or the the way used for `methods`, it has no effect: mock functions aren't called)
