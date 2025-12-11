import prediction


def test_make_prediction_simple():
    """A simple test to check if make_prediction returns a float.
    This test has been modified to include all 5 required input features 
    expected by the make_prediction function.
    """
    # The keys here must match the keys used in kwargs extraction in prediction.py
    result = prediction.make_prediction(
        tenure=2, 
        MonthlyCharges=12.3, 
        TechSupport=0,               # Corrected key from TechSupport_yes to TechSupport
        ContractMonthToMonth=1,      # Added missing key
        FiberOptic=0                 # Added missing key
    )
    assert isinstance(result, float)