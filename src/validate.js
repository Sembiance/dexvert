import { assert, assertStrictEquals } from "https://deno.land/std@0.110.0/testing/asserts.ts";

export function validateClass(o, schema)
{
	const extraProperties = Object.keys(o).subtractAll([...Object.keys(schema), ...o.baseKeys, "baseKeys"]);
	if(extraProperties.length)
		throw new Error(`class [${o.constructor.name}] has extra unsupported properties: [${extraProperties.join("], [")}]`);

	for(const [propid, prop] of Object.entries(schema))
	{
		if(!Object.hasOwn(o, propid))
		{
			if(prop.required)
				throw new Error(`class [${o.constructor.name}] is missing required property [${propid}]`);
			
			continue;
		}

		const value = o[propid];

		// validate the property type
		if(prop.type)
		{
			if(Array.isArray(prop.type))
			{
				assert(Array.isArray(value), `class [${o.constructor.name}].[${propid}] expected to be an array, but got [${typeof value}]`);
				value.forEach(v =>
				{
					const typeMatches = prop.type.filter(t => typeof t==="string");
					const instanceMatches = prop.type.filter(t => typeof t!=="string");
					if(!typeMatches.includes(typeof v) && !instanceMatches.some(instanceMatch => v instanceof instanceMatch))
						throw new Error(`class [${o.constructor.name}].[${propid}] value [${v}] expected to be one of type [${prop.type.map(t => (typeof t==="string" ? t : t.name)).join("], [")}] but got [${typeof v}]`);
				});
			}
			else
			{
				assertStrictEquals(typeof value, prop.type, `class [${o.constructor.name}].[${propid}] expected to be type [${prop.type}] but got [${typeof value}]`);
			}
		}

		// validate that the property is a valid URL
		if(prop.url)
			assert((new URL(value)) instanceof URL, `class [${o.constructor.name}].[${propid}] expected to be a valid URL but it was not`);
		
		// validate that the property has a spcific value
		if(prop.enum)
			assert(prop.enum.includes(value), `class [${o.constructor.name}].[${propid}] expected to be one of value [${prop.enum.join("], [")}] but got [${value}]`);

		// validate that the property value is a given length
		if(prop.length)
			assertStrictEquals(prop.length, value.length, `class [${o.constructor.name}].[${propid}] value [${value}] expected to be [${prop.length}] long but is [${value.length}] long`);
	}
}
