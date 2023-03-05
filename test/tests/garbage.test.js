import {xu} from "xu";
import {path, assert, assertEquals} from "std";
import {classifyImage} from "/mnt/compendium/DevLab/dexvert/src/tensorUtil.js";

const GARBAGE = ["xZubmS7uwg4ErYTFmioz8p2tsMLmT4jo.png", "xhXMpIrYnUHxDOayEH0qnb8xtF0k91o4.png", "xk2O5GM1umw3gWKgicGpnQ31OS7feV6X.png", "xnyLQkvJAumat6eNxsDy9DKjYzwqMdjc.png", "xw9uVCmh3Zov3ygiVgWfbBeSMnmURnUH.png", "y0Ym3qtRklfsdRWXmfHlzPsWeIR7PXny.png", "y1RXtPWp92cxfCByh1sgzx3jXWf0keM7.png"];
const NOT_GARBAGE = ["yii68COEWswquliTAPY3jHv85DhyaKUL.png", "yjINulmPEA6E49hXYOTT8sshDFRxKvSv.png", "yl4ttyEmzCM9mxFIwr53CFlN9jbaHeWj.png", "yn4IJVbe8HziVXK6xvW1RWIfcSeOokIt.png", "yr8hltX6A0awq8R8mZUSkQKhIXTDHB7g.png", "yrNnUvHXYQ8j7ADJfbv24FSqzkXjAXmE.png", "ys7NCEaFt9QIoUaWBm0nOB9A1SLanGXQ.png"];

Deno.test("garbage", async () => assertEquals([1, 1, 3.1692634627766836e-12, 1, 1, 1, 1], await GARBAGE.parallelMap(async v => await classifyImage(path.join(xu.dirname(import.meta), "garbage", v), "garbage"))));	// eslint-disable-line unicorn/numeric-separators-style

Deno.test("notGarbage", async () => assert((await NOT_GARBAGE.parallelMap(async v => await classifyImage(path.join(xu.dirname(import.meta), "notGarbage", v), "garbage"))).every(v => v===0)));

