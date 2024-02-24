# PURE-Data-Standard
PURE Data Standard is a comprehensive resource for developing and implementing a precision-based approach to content extraction and summarization. A unified framework for extracting clear, unbiased, and concise summaries from various types of content, including news articles, research papers, and other textual materials.


## Example
An example of a sensationalized news report about a hypothetical natural disaster with provided equivalent representation in the PURE data standard format.

**Sensationalized News Report:**
```plaintext
Title: "Apocalyptic Tornado Strikes Coastal City - Death Toll Rising!"

Date: February 18, 2024

Location: Coastal City, Region X, Country Y

Report:
In a cataclysmic event of unprecedented proportions, a monstrous tornado ripped through the coastal city, leaving a path of destruction in its wake. Scenes of chaos and devastation unfolded as homes were torn apart, cars tossed like toys, and lives shattered in an instant. Rescue teams battled against the odds to save survivors trapped beneath the rubble, while the death toll continued to climb by the hour. Experts warn that this could be just the beginning of a new era of extreme weather events brought on by climate change, leaving residents in fear and uncertainty about what the future may hold.
```

**PURE Standard Equivalent:**
```json
{
  "type": "News",
  "date_time": "2024-02-18",
  "location": {
    "city": "Coastal City",
    "region": "Region X",
    "country": "Country Y"
  },
  "event_type": "Natural Disaster",
  "specific_event": "Tornado",
  "affected_population": "Unknown",
  "casualties": {
    "injuries": "10+",
    "fatalities": 2
  },
  "damage": {
    "homes": "10+",
    "businesses": "10+"
  },
  "references": ["ref-a", "ref-b"]
}
```

In the PURE standard equivalent, the information is presented in a factual and objective manner, without sensationalism or speculative commentary. Each attribute provides specific details about the natural disaster event, such as the type of event, location, casualties, and damage. This representation adheres to the principles of the PURE data standardization framework, ensuring replicability and consistency in data reporting.


todo:

- introduce a single type entity (data block) which allows either referenced or children datablocks
- python module
- blockchain technology considerations