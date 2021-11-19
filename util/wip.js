import {path} from "std";
console.log(path.basename((new URL(import.meta.url)).pathname, ".js"));
