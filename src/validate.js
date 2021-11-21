import {assert, assertStrictEquals} from "std";

export function validateClass(o, schema)
{
	const prefix = `class [${o.constructor.name}]`;
	const suffix = `for class ${JSON.stringify(o)}`;
	return validate(prefix, suffix, o, schema);
}

export function validateObject(o, schema)
{
	return validate(`object`, `for object ${JSON.stringify(o)}`, o, schema);
}

function validate(basePrefix, suffix, o, schema)
{
	let prefix = basePrefix;
	
	const extraProperties = Object.keys(o).subtractAll([...Object.keys(schema), ...(o.baseKeys || []), "baseKeys"]);
	if(extraProperties.length)
		throw new Error(`${prefix} has extra unsupported properties: [${extraProperties.join("], [")}] ${suffix}`);

	for(const [propid, prop] of Object.entries(schema))
	{
		const value = o[propid];
		if(typeof value==="undefined")
		{
			if(prop.required)
				throw new Error(`${prefix} is missing required property [${propid}] ${suffix}`);
			
			continue;
		}

		prefix = `${basePrefix}.[${propid}]`;

		// validate the property type
		if(prop.type)
		{
			if(Array.isArray(prop.type))
			{
				assert(Array.isArray(value), `${prefix} expected to be an array, but got [${typeof value}] ${suffix}`);
				value.forEach(v =>	// eslint-disable-line no-loop-func
				{
					const typeMatches = prop.type.filter(t => typeof t==="string");
					const instanceMatches = prop.type.filter(t => typeof t!=="string");
					if(!typeMatches.includes(typeof v) && !instanceMatches.some(instanceMatch => v instanceof instanceMatch))
						throw new Error(`${prefix} value [${v}] expected to be one of type [${prop.type.map(t => (typeof t==="string" ? t : t.name)).join("], [")}] but got [${typeof v}] ${suffix}`);
					
					if(prop.type.includes("string") && typeof v==="string")
						assert(v.length>0, `${prefix} array value [${v}] expected to to not be empty ${suffix}`);
				});
			}
			else
			{
				if(typeof prop.type==="string")
					assertStrictEquals(typeof value, prop.type, `${prefix} expected to be type [${prop.type}] but got [${typeof value}] ${suffix}`);
				else
					assert(value instanceof prop.type, `${prefix} expected to be instance [${prop.type}] but got ${value.constructor.name} ${suffix}`);
			}
		}

		if(prop.types && !prop.types.some(type => (typeof type==="string" ? (typeof value===type) : (value instanceof type))))
			throw new Error(`${prefix} value [${value}] expected to be one of type [${prop.types.map(t => (typeof t==="string" ? t : t.name)).join("], [")}] but got [${typeof value}] ${suffix}`);

		// validate that the property is a valid URL
		if(prop.url)
			assert((new URL(value)) instanceof URL, `${prefix} expected to be a valid URL but it was not ${suffix}`);
		
		// validate that the property has a spcific value
		if(prop.enum && prop.enum.length>0)
		{
			if(Array.isArray(value))
				assertStrictEquals(value.filter(v => !prop.enum.includes(v)).length, 0, `${prefix} expected to contain one of value [${prop.enum.join("], [")}] but got [${value}] ${suffix}`);
			else
				assert(prop.enum.includes(value), `${prefix} expected to be one of value [${prop.enum.join("], [")}] but got [${value}] ${suffix}`);
		}

		// validate that the property value is a given length
		if(prop.length)
		{
			if(Array.isArray(prop.length))
			{
				assert(value.length>=prop.length[0], `${prefix} value [${value}] expected to be at least ${prop.length[0]} long but is [${value.length}] long ${suffix}`);
				if(prop.length.length>1)
					assert(value.length<=prop.length[1], `${prefix} value [${value}] expected to be less than ${prop.length[1]} long but is [${value.length}] long ${suffix}`);
			}
			else
			{
				assertStrictEquals(prop.length, value.length, `${prefix} value [${value}] expected to be [${prop.length}] long but is [${value.length}] long ${suffix}`);
			}
		}
		
		// validate that the property value falls within a given range
		if(prop.range)
		{
			assert(value>=prop.range[0]);
			if(prop.range.length>1)
				assert(value<=prop.range[1]);
		}
		
		// by default, strings and arrays must not be empty
		if(!prop.allowEmpty && (typeof value==="string" || Array.isArray(value)))
			assert(value.length>0, `${prefix} value [${value}] expected to to not be empty ${suffix}`);
	}
}
