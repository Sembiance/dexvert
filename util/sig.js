import {xu} from "xu";
import { delay } from "https://deno.land/std@0.111.0/async/mod.ts";
import { onSignal } from "https://deno.land/std@0.113.0/signal/mod.ts";

const handle = onSignal("SIGINT", () =>
{
	xu.log`got sigint`;
	handle.dispose(); // de-register from receiving further events.
});

await delay(xu.MINUTE);
