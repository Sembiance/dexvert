import {Format} from "../../Format.js";

export class simisShape extends Format
{
	name           = "SIMIS Shape";
	ext            = [".s"];
	forbidExtMatch = true;
	magic          = ["SIMIS Shape", /^geArchive: ACE_SIMIS( |$)/];
	converters     = ["poly2glb[type:simisShape]"]; // would work, but not needed since poly2glb handles the SIMIS format too: "gameextractor[codes:ACE_SIMIS][renameOut] -> poly2glb[type:simisShape]"];
}
