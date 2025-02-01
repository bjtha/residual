from residual.services import *

def test_register_service() -> None:

    @register_service
    class TestService(ServiceBaseClass):
        def run(self, inputs):
            ...

    assert service_registry == {'TestService': TestService}