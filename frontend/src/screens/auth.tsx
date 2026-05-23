import { useState } from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { LogIn, UserPlus, Wrench } from 'lucide-react-native';

import {
  Badge,
  BodyText,
  Field,
  Header,
  Panel,
  PrimaryButton,
  Screen,
  SectionTitle,
} from '../components/ui';
import { theme } from '../theme/tokens';
import type { AuthActions } from '../types';

type AuthMode = 'login' | 'register';

export function AuthScreen({ auth, notice }: { auth: AuthActions; notice?: string | null }) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail || !password || submitting) return;

    setSubmitting(true);
    setError(null);
    try {
      if (mode === 'register') {
        await auth.register({
          email: trimmedEmail,
          password,
          fullName: fullName.trim(),
        });
      } else {
        await auth.login({ email: trimmedEmail, password });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo iniciar sesion.');
    } finally {
      setSubmitting(false);
    }
  };

  const disabled = !email.trim() || !password || submitting;

  return (
    <Screen>
      <Header title="CoolAgent" eyebrow="Acceso tecnico" right={<Badge tone="accent">API</Badge>} />

      <Panel accent>
        <View style={{ gap: 14 }}>
          {notice ? (
            <View
              style={{
                backgroundColor: theme.color.warningSoft,
                borderRadius: theme.radius.md,
                padding: 10,
              }}
            >
              <Text style={{ color: theme.color.warning, fontSize: 13, lineHeight: 18 }}>{notice}</Text>
            </View>
          ) : null}

          <View style={{ flexDirection: 'row', gap: 8 }}>
            {(['login', 'register'] as const).map((item) => (
              <Pressable
                key={item}
                onPress={() => {
                  setMode(item);
                  setError(null);
                }}
                style={{
                  backgroundColor: mode === item ? theme.color.accent : theme.color.surfaceAlt,
                  borderRadius: theme.radius.pill,
                  paddingHorizontal: 12,
                  paddingVertical: 8,
                }}
              >
                <Text
                  style={{
                    color: mode === item ? theme.color.black : theme.color.text,
                    fontWeight: '700',
                  }}
                >
                  {item === 'login' ? 'Entrar' : 'Registro'}
                </Text>
              </Pressable>
            ))}
          </View>

          {mode === 'register' ? (
            <Field
              autoCapitalize="words"
              label="Nombre"
              onChangeText={setFullName}
              placeholder="Ricardo Tecnico"
              textContentType="name"
              value={fullName}
            />
          ) : null}
          <Field
            autoCapitalize="none"
            keyboardType="email-address"
            label="Email"
            onChangeText={setEmail}
            placeholder="tecnico@example.com"
            textContentType="emailAddress"
            value={email}
          />
          <Field
            autoCapitalize="none"
            label="Password"
            onChangeText={setPassword}
            placeholder="Minimo 8 caracteres"
            secureTextEntry
            textContentType={mode === 'register' ? 'newPassword' : 'password'}
            value={password}
          />

          {error ? (
            <View
              style={{
                backgroundColor: theme.color.dangerSoft,
                borderRadius: theme.radius.md,
                padding: 10,
              }}
            >
              <Text style={{ color: theme.color.danger, fontSize: 13, lineHeight: 18 }}>{error}</Text>
            </View>
          ) : null}

          <PrimaryButton
            disabled={disabled}
            icon={submitting ? undefined : mode === 'register' ? UserPlus : LogIn}
            label={
              submitting
                ? mode === 'register'
                  ? 'Creando cuenta...'
                  : 'Entrando...'
                : mode === 'register'
                  ? 'Crear cuenta'
                  : 'Entrar'
            }
            onPress={submit}
          />
          {submitting ? (
            <View style={{ alignItems: 'center', flexDirection: 'row', gap: 10 }}>
              <ActivityIndicator color={theme.color.accent} />
              <BodyText muted>Validando con el backend...</BodyText>
            </View>
          ) : null}
        </View>
      </Panel>

      <SectionTitle>Desarrollo local</SectionTitle>
      <Panel>
        <View style={{ gap: 12 }}>
          <BodyText muted>
            Usa el backend local para una sesion real. El modo local usa datos mock y no sincroniza casos.
          </BodyText>
          <PrimaryButton
            icon={Wrench}
            label="Continuar local"
            onPress={auth.continueLocal}
            variant="ghost"
          />
        </View>
      </Panel>
    </Screen>
  );
}
