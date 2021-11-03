/* eslint-disable no-restricted-syntax */
import PQueue from "https://deno.land/x/p_queue@1.0.1/mod.ts";
import { delay } from "https://deno.land/std@0.111.0/async/mod.ts";

async function someFunc(i)
{
	console.log(`${i}`);
	await delay(2000);
	return i;
}

//const r = await Promise.all([queue.add(() => someFunc(1)), queue.add(() => someFunc(2)), queue.add(() => someFunc(3)), queue.add(() => someFunc(4))]);

//const r = await Promise.all([1, 2, 3, 4, 5].map(v => queue.add(() => someFunc(v))));
//const r = await Promise.all([1, 2, 3, 4, 5].map(v => queue.add(() => someFunc(v))));
//const r = await queue.addAll([1, 2, 3, 4, 5].map(v => () => someFunc(v)));


//const test = [].map(v => () => someFunc(v));
//console.log(test);



const r = await [1, 2, 3, 4, 5].parallelMap(someFunc, 0);
console.log({r});
