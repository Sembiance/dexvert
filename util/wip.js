import {xu} from "xu";
import {delay} from "std";

const {rid} = await Deno.open("/tmp/test", {write : true, createNew : true}).catch(() => {});
console.log({rid});
await delay(xu.SECOND*1);
Deno.close(rid);
