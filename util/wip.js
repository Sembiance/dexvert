/* eslint-disable no-unused-vars */
import {xu} from "xu";
import {runUtil, fileUtil} from "xutil";
import {path, delay} from "std";


const test = await Deno.lstat("/tmp/berjkhbkerbner").catch(() => {});
console.log(test);
