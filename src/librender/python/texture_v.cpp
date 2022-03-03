#include <mitsuba/render/interaction.h>
#include <mitsuba/render/texture.h>
#include <mitsuba/core/properties.h>
#include <mitsuba/python/python.h>


/// Trampoline for derived types implemented in Python
MTS_VARIANT class PyTexture : public Texture<Float, Spectrum> {
public:
    MTS_IMPORT_BASE(Texture, m_id)
    MTS_IMPORT_TYPES(Texture)

    PyTexture(const Properties &props) : Texture(props) { }

    UnpolarizedSpectrum eval(const SurfaceInteraction3f &si,
                             Mask active = true) const override {
        using Return = UnpolarizedSpectrum;
        PYBIND11_OVERLOAD_PURE(Return, Texture, eval, si, active);
    }

    std::pair<Wavelength, UnpolarizedSpectrum>
    sample_spectrum(const SurfaceInteraction3f &si,
                    const Wavelength &sample,
                    Mask active = true) const override {
        using Return = std::pair<Wavelength, UnpolarizedSpectrum>;
        PYBIND11_OVERLOAD_PURE(Return, Texture, sample_spectrum, si, sample, active);
    }

    Wavelength pdf_spectrum(const SurfaceInteraction3f &si,
                            Mask active = true) const override {
        using Return = Wavelength;
        PYBIND11_OVERLOAD_PURE(Return, Texture, pdf_spectrum, si, active);
    }

    std::pair<Point2f, Float> sample_position(const Point2f &sample,
                                              Mask active = true) const override {
        using Return = std::pair<Point2f, Float>;
        PYBIND11_OVERLOAD_PURE(Return, Texture, sample_position, sample, active);
    }

    ScalarFloat mean() const override {
        using Return = ScalarFloat;
        PYBIND11_OVERLOAD_PURE(Return, Texture, mean);
    }

    std::string to_string() const override {
        using Return = std::string;
        PYBIND11_OVERLOAD_PURE(Return, Texture, to_string);
    }

    /*Float pdf_position(const Point2f &p, Mask active = true) const override {
        PYBIND11_OVERLOAD_PURE(Float, Texture, pdf_position, p, active);
    }


    Float eval_1(const SurfaceInteraction3f &si, Mask active = true) const override {
        PYBIND11_OVERLOAD_PURE(Float, Texture, eval_1, si, active);
    }*/
};

MTS_PY_EXPORT(Texture) {
    MTS_PY_IMPORT_TYPES()
    using PyTexture = PyTexture<Float, Spectrum>;

    auto texture = py::class_<Texture, PyTexture, ref<Texture>>(m, "Texture", D(Texture))
        .def(py::init<const Properties&>())
        .def_readwrite("m_id", &PyTexture::m_id);

    MTS_PY_REGISTER_OBJECT("register_texture", Texture)

    /*MTS_PY_CLASS(Texture, Object)
        .def_static("D65", &Texture::D65, "scale"_a = 1.f)
        .def("mean", &Texture::mean, D(Texture, mean))
        .def("is_spatially_varying", &Texture::is_spatially_varying,
             D(Texture, is_spatially_varying))
        .def("eval",
            vectorize(&Texture::eval),
            "si"_a, "active"_a = true, D(Texture, eval))
        .def("eval_1",
            vectorize(&Texture::eval_1),
            "si"_a, "active"_a = true, D(Texture, eval_1))
        .def("eval_1_grad",
            vectorize(&Texture::eval_1_grad),
            "si"_a, "active"_a = true, D(Texture, eval_1_grad))
        .def("eval_3",
            vectorize(&Texture::eval_3),
            "si"_a, "active"_a = true, D(Texture, eval_3))
        .def("sample_spectrum",
            vectorize(&Texture::sample_spectrum),
            "si"_a, "sample"_a, "active"_a = true, D(Texture, sample_spectrum))
        .def("pdf_spectrum", &Texture::pdf_spectrum,
            "si"_a, "active"_a = true, D(Texture, pdf_spectrum))
        .def("sample_position",
            vectorize(&Texture::sample_position),
            "sample"_a, "active"_a = true, D(Texture, sample_position))
        .def("pdf_position",
            vectorize(&Texture::pdf_position),
            "p"_a, "active"_a = true, D(Texture, pdf_position));
}*/
}



MTS_PY_EXPORT(Volume) {
    MTS_PY_IMPORT_TYPES(Volume)
    MTS_PY_CLASS(Volume, Object)
        .def("eval",
            vectorize(&Volume::eval),
            "it"_a, "active"_a = true, D(Volume, eval))
        .def("eval_1",
            vectorize(&Volume::eval_1),
            "it"_a, "active"_a = true, D(Volume, eval_1))
        .def("eval_3",
            vectorize(&Volume::eval_3),
            "it"_a, "active"_a = true, D(Volume, eval_3))
        .def("eval_gradient",
            vectorize(&Volume::eval_gradient),
            "it"_a, "active"_a = true, D(Volume, eval_gradient))
        .def("max",
            &Volume::max,
            D(Volume, max))
        .def("bbox",
            &Volume::bbox,
            D(Volume, bbox))
        .def("resolution",
            &Volume::resolution,
            D(Volume, resolution));
}
