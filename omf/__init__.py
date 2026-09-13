"""optical-metrology-fitter (omf)

A transfer-matrix forward model and inverse solver for thin-film optical
metrology, with an explicit uncertainty budget.

Convention: exp(-i omega t), n_tilde = n + i k, Im(k_z) >= 0.
"""
from .core import coh_tmm, fresnel_rt, kz_from_index, snell_angles, psi_delta
from .materials import (n_air, n_vacuum, n_sio2, n_bk7, n_si, n_si_aspnes,
                        n_constant, n_pnipam_swollen, n_water,
                        build_n_list, MATERIALS)
from .fitter import FilmModel, FitResult, EllipsometryModel
from .uncertainty import numerical_jacobian, fisher_information, crlb, monte_carlo_fit

__version__ = "0.3.0"
__all__ = [
    "coh_tmm", "fresnel_rt", "kz_from_index", "snell_angles", "psi_delta",
    "n_air", "n_vacuum", "n_sio2", "n_bk7", "n_si", "n_si_aspnes", "n_constant",
    "n_pnipam_swollen", "n_water",
    "build_n_list", "MATERIALS",
    "FilmModel", "FitResult", "EllipsometryModel",
    "numerical_jacobian", "fisher_information", "crlb", "monte_carlo_fit",
]
