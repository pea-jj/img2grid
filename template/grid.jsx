{%- set grid_schema, operation_schema, filter_schema = schema['grid_schema'], schema['operation_schema'], schema['filter_schema'] -%}
import React from 'react';
const culumns =  [
{%- for item in grid_schema["grid_column"] -%}{
    title: "{{ item.title }}",
    bodyRender: data => {}
},{%- endfor -%}
];