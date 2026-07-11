import 'user.dart';

sealed class AuthState {
  const AuthState();
}

class Initial extends AuthState {
  const Initial();
}

class Authenticated extends AuthState {
  final User user;
  const Authenticated(this.user);
}

class Unauthenticated extends AuthState {
  const Unauthenticated();
}

class Loading extends AuthState {
  const Loading();
}

class AuthError extends AuthState {
  final String message;
  const AuthError(this.message);
}
