//alert('Hello, world!')
//const theNumber = 1
//let yourName = 'Ben'

/*
if (theNumber === 1) {
  let yourName = 'Leo'
  alert(yourName)
}

alert(yourName)

console.time('myTimer')
console.count('counter1')
console.log('A normal log message')
console.warn('Warning: something bad might happen')
console.error('Something bad did happen!')
console.count('counter1')
console.log('All the things above took this long to happen:')
console.timeEnd('myTimer')

function sayHello(yourName) {
  if (yourName === undefined) {
      console.log('Hello, no name')
  } else {
       console.log('Hello, ' + yourName)
  }
}

const yourName = 'Brock'  // Put your name here

console.log('Before setTimeout')

setTimeout(() => {
    sayHello(yourName)
    console.log('Just got back from sayHello')
  }, 2000
)

console.log('After setTimeout')

for(let i = 0; i < 10; i += 1) {
  console.log('for loop i: ' + i)
}

let j = 0
while(j < 10) {
  console.log('while loop j: ' + j)
  j += 1
}

let k = 10

do {
  console.log('do while k: ' + k)
} while(k < 10)

const numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

numbers.forEach((value => {
  console.log('For each value ' + value)
}))

const doubled = numbers.map(value => value * 2)

console.log('Here are the doubled numbers')

console.log(doubled)

class Greeter {
  constructor (name) {
    this.name = name
  }

  getGreeting () {
    if (this.name === undefined) {
      return 'Hello, no name'
    }

    return 'Hello, ' + this.name
  }

  showGreeting (greetingMessage) {
    console.log(greetingMessage)
  }

  greet () {
    this.showGreeting(this.getGreeting())
  }
}

const g = new Greeter('Patchy')  // Put your name here if you like
g.greet()

class DelayedGreeter extends Greeter {
  delay = 2000

  constructor (name, delay) {
    super(name)
    if (delay !== undefined) {
      this.delay = delay
    }
  }

  greet () {
    setTimeout(
      () => {
        this.showGreeting(this.getGreeting())
      }, this.delay
    )
  }
}

const dg2 = new DelayedGreeter('Patchy 2 Seconds')
dg2.greet()

const dg1 = new DelayedGreeter('Stroller 1 Second', 1000)
dg1.greet()

*/

function resolvedCallback(data) {
  console.log('Resolved with data ' +  data)
}

function rejectedCallback(message) {
  console.log('Rejected with message ' + message)
}

/*
The function that other code will call is lazyAdd, but we define 
another function inside it called doAdd which contains the actual 
code to do the addition. We need to do this because the function 
we pass to the Promise class must only take resolve and reject 
functions as parameters. We could not pass a function to Promise 
that takes the numbers to add and the resolve and reject functions.

Below doAdd is the function that will be passed to
the Promise class.  doAdd takes resolve and reject functions as
parameters.
*/
const lazyAdd = function (a, b) {
  const doAdd = (resolve, reject) => {
    if (typeof a !== "number" || typeof b !== "number") {
      reject("a and b must both be numbers")
    } else {
      const sum = a + b
      resolve(sum)
    }
  }
  /*
   The function we pass to the Promise class must only take 
   resolve and reject functions as parameters.  Below, we 
   instantiate a promise using doAdd as the parameter.
  */
  return new Promise(doAdd)
}

/*
Below lazyAdd(3,4) returns a Promise object to p.  This is per the 
return new Promise(doAdd) at the end of the lazyAdd function.
See above.  
lazyAdd is the first callback. See below for the other two callbacks.
What we’ve defined so far could be considered the “producer” 
side of the Promise system.
*/

const p = lazyAdd(3, 4)

/*
We need to define two more callback functions. We know from documentation,
or inspecting source code, that the resolve function accepts a single
argument, the result of the addition. We’d also know the reject function
also accepts a single argument, a string that describes why the promise
was rejected. It is up to us as the consumer to decide how to deal 
with the results.

How do we actually get the lazyAdd() function to give us a result? We use
the then() method on a Promise. The then() method has the same signature 
as whatever function was passed to the Promise constructor. In our case, 
this was the doAdd() internal function, and we know it accepts resolve 
and reject callback functions. Once the then() method is called, 
whether it resolves or rejects, the Promise is then called (considered)
settled.
*/

//resolvedCallback and rejectedCallbackk are the other two callback functions
p.then(resolvedCallback, rejectedCallback)

lazyAdd("nan", "alsonan").then(resolvedCallback, rejectedCallback)