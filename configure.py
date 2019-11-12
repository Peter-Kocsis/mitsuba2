import json
from collections import OrderedDict

print('Reading mitsuba.conf...')
with open("mitsuba.conf", "r") as f:
    # Load while preserving order of keys
    configurations = json.load(f, object_pairs_hook=OrderedDict)

# Let's start with some validation
assert('enabled' in configurations and
       'default' in configurations)
assert(type(configurations['default']) is str)
assert(type(configurations['enabled']) is list)

# Extract enabled configurations
enabled = []
for name in configurations['enabled']:
    if name not in configurations:
        raise Exception('"enabled" refers to an unknown configuration "%s"' % name)
    item = configurations[name]
    spectrum = item['spectrum'].replace('Float', item['float'])
    enabled.append((name, item['float'], spectrum))

if len(enabled) == 0:
    raise Exception("There must be at least one enabled build configuration!")

# Use first configuration if default mode is not specified
default_mode = configurations.get('default', enabled[0][0])

# Write header file
fname = "include/mitsuba/core/config.h"
with open(fname, 'w') as f:
    def w(s):
        f.write(s.ljust(75) + ' \\\n')
    f.write('#pragma once\n\n')
    f.write('#include <mitsuba/core/fwd.h>\n\n')

    w('#define MTS_CONFIGURATIONS')
    for index, (name, float_, spectrum) in enumerate(enabled):
        w('    "%s\\n"' % name)
    f.write('\n\n')

    w('#define MTS_CONFIGURATIONS_INDENTED')
    for index, (name, float_, spectrum) in enumerate(enabled):
        w('    "            %s\\n"' % name)
    f.write('\n\n')

    w('#define MTS_DEFAULT_MODE "%s"' % default_mode)
    f.write('\n\n')

    w('#define MTS_INSTANTIATE_OBJECT(Name)')
    for index, (name, float_, spectrum) in enumerate(enabled):
        w('    template class MTS_EXPORT Name<%s, %s>;' % (float_, spectrum))
    f.write('\n\n')

    w('#define MTS_INSTANTIATE_STRUCT(Name)')
    for index, (name, float_, spectrum) in enumerate(enabled):
        w('    template struct MTS_EXPORT Name<%s, %s>;' % (float_, spectrum))
    f.write('\n\n')

    w('#define MTS_IMPLEMENT_PLUGIN(Name, Parent, Descr)')
    w('    extern "C" {')
    w('        MTS_EXPORT const char *plugin_name() { return #Name; }')
    w('        MTS_EXPORT const char *plugin_descr() { return Descr; }')
    w('    }')
    w('    MTS_INSTANTIATE_OBJECT(Name)')
    f.write('\n\n')

    w('#define MTS_PY_DECLARE_VARIANTS(name)')
    for index, (name, float_, spectrum) in enumerate(enabled):
        # for packets of float, the bindings should use the vectorize wrapper on dynamic arrays
        float_p = float_
        spectrum_p = spectrum
        if float_.startswith("Packet"):
            float_x = "DynamicArray<%s>" % float_
            spectrum = spectrum.replace(float_, float_x)
            float_ = float_x
        w('    extern void python_export_variants_%s_##name(py::module &);' % (name))
    f.write('\n\n')

    w('#define MTS_PY_DEF_SUBMODULE_VARIANTS(lib)')
    for index, (name, float_, spectrum) in enumerate(enabled):
        w('    auto __submodule__%s =  m.def_submodule("%s").def_submodule(#lib);' % (name, name))
    f.write('\n\n')

    w('#define MTS_PY_IMPORT_VARIANTS(name)')
    for index, (name, float_, spectrum) in enumerate(enabled):
        # for packets of float, the bindings should use the vectorize wrapper on dynamic arrays
        float_p = float_
        spectrum_p = spectrum
        if float_.startswith("Packet"):
            float_x = "DynamicArray<%s>" % float_
            spectrum = spectrum.replace(float_, float_x)
            float_ = float_x
        w('    python_export_variants_%s_##name(__submodule__%s);' % (name, name))
    f.write('\n\n')

    w('#define MTS_PY_EXPORT_VARIANTS(name)')
    w('    template <typename Float, typename Spectrum,')
    w('              typename FloatP, typename SpectrumP>')
    w('    void instantiate_##name(py::module m);')
    w('')
    for index, (name, float_, spectrum) in enumerate(enabled):
        # for packets of float, the bindings should use the vectorize wrapper on dynamic arrays
        float_p = float_
        spectrum_p = spectrum
        if float_.startswith("Packet"):
            float_x = "DynamicArray<%s>" % float_
            spectrum = spectrum.replace(float_, float_x)
            float_ = float_x
        w('    void python_export_variants_%s_##name(py::module &m) {' % (name))
        w('        instantiate_##name<%s, %s, %s, %s>(m);' % (float_, spectrum, float_p, spectrum_p))
        w('    }')
    w('')
    w('    template <typename Float, typename Spectrum,')
    w('              typename FloatP, typename SpectrumP>')
    w('    void instantiate_##name(py::module m)')
    f.write('\n\n')


    w('#define MTS_ROUTE_MODE(mode, function, ...)')
    w('    [&]() {')
    for index, (name, float_, spectrum) in enumerate(enabled):
        iff = 'if' if index == 0 else 'else if'
        w('        %s (mode == "%s")' % (iff, name))
        w('            return function<%s, %s>(__VA_ARGS__);' % (float_, spectrum))
    w('        else')
    w('            Throw("Unsupported mode: %s", mode);')
    w('    }()')
    f.write('\n\n')

    w('#define PY_CAST_VARIANTS(Name)')
    for index, (name, float_, spectrum) in enumerate(enabled):
        spectrum = spectrum.replace('Float', float_)
        w('    if (auto tmp = dynamic_cast<Name<%s, %s> *>(o); tmp)' % (float_, spectrum))
        w('        return py::cast(tmp);')
    f.write('\n\n')

    f.write('NAMESPACE_BEGIN(mitsuba)\n')
    f.write('NAMESPACE_BEGIN(detail)\n')
    f.write('template <typename Float, typename Spectrum_> constexpr const char *get_variant() {\n')
    for index, (name, float_, spectrum) in enumerate(enabled):
        f.write('    %sif constexpr (std::is_same_v<Float, %s> && std::is_same_v<Spectrum_, %s>)\n' % ('else ' if index > 0 else '', float_, spectrum))
        f.write('        return "%s";\n' % name)
    f.write('    else\n')
    f.write('        return "";\n')
    f.write('}\n')
    f.write('NAMESPACE_END(detail)\n')
    f.write('NAMESPACE_END(mitsuba)\n')

print('Generated configuration header: ' + fname)
